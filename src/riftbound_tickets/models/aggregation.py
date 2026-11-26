"""Exact ticket capacity counterfactuals. No policy permission or Swiss forecast.

Historical ranks can be sampled without replacement. Vegas and separate
weekend paths use explicitly independent blocks; a shared team outcome is one
joint block and must never be duplicated as independent individual awards.
"""
from collections import defaultdict
from fractions import Fraction as F
from math import comb

from .individual import convolution


def check(pmf):
    if not pmf or sum(pmf.values())!=1 or any(type(t) is not int or t<0 or p<0 for t,p in pmf.items()):
        raise ValueError('Normalized nonnegative integer ticket PMF required')


def joint_from_pmf(pmf):
    check(pmf)
    return {(t,t//40,int(t>=40)):p for t,p in pmf.items() if p}


def joint_convolve(a,b):
    result=defaultdict(F)
    for x,p in a.items():
        for y,q in b.items():
            if q: result[tuple(u+v for u,v in zip(x,y))]+=p*q
    return dict(result)


def independent_joint(pmf,n):
    check(pmf)
    if type(n) is not int or n<1: raise ValueError('Positive integer group size required')
    result={(0,0,0):F(1)}
    block=joint_from_pmf(pmf)
    for _ in range(n): result=joint_convolve(result,block)
    return result


def without_replacement(counts,n):
    """Multivariate hypergeometric, unordered category compositions; no MC."""
    if any(type(t) is not int or t<0 or type(c) is not int or c<0 for t,c in counts.items()):
        raise ValueError('Nonnegative integer award counts required')
    N=sum(counts.values())
    if type(n) is not int or not 1<=n<=N: raise ValueError('Invalid sample size')
    categories=[(t,c) for t,c in sorted(counts.items()) if c]
    result=defaultdict(F)
    denom=comb(N,n)
    def enumerate_counts(i,left,total,units,qual,ways):
        if i==len(categories):
            if left==0: result[(total,units,qual)]+=F(ways,denom)
            return
        t,c=categories[i]
        for k in range(min(c,left)+1):
            enumerate_counts(i+1,left-k,total+k*t,units+k*(t//40),qual+k*int(t>=40),ways*comb(c,k))
    enumerate_counts(0,n,0,0,0,1)
    if sum(result.values())!=1: raise ValueError('Hypergeometric mass lost')
    return dict(result)


def group_metrics(joint,n):
    if sum(joint.values())!=1 or n<1: raise ValueError('Invalid group joint distribution')
    mean=sum(F(t)*p for (t,_,_),p in joint.items())
    no_success=sum((p for (_,_,q),p in joint.items() if q>0),F(0))
    pooled=sum((p for (t,_,_),p in joint.items() if t>=40),F(0))
    own=sum(F(u)*p for (_,u,_),p in joint.items())
    full=sum(F(t//40)*p for (t,_,_),p in joint.items())
    residual=sum(F(t%40)*p for (t,_,_),p in joint.items())
    fragments=sum(F(t-40*u)*p for (t,u,_),p in joint.items())
    if mean!=40*full+residual or mean!=40*own+fragments: raise ValueError('Ticket conservation failed')
    return {'group_size':n,'expected_total_tickets':mean,'p_any_individual_40':no_success,
        'p_all_individual_40':sum((p for (_,_,q),p in joint.items() if q==n),F(0)),
        'expected_qualifying_individuals':sum(F(q)*p for (_,_,q),p in joint.items()),
        'random_member_individual_40_probability':sum(F(q)*p for (_,_,q),p in joint.items())/n,
        'p_aggregate_40':pooled,'prioritized_recipient_full_pool_probability':pooled,
        'p_full_pool_capacity_for_everyone':sum((p for (t,_,_),p in joint.items() if t>=40*n),F(0)),
        'incremental_success_probability':pooled-no_success,
        'relative_success_lift':pooled/no_success-1 if no_success else None,
        'expected_units_no_pool':own,'expected_units_full_pool':full,
        'units_no_pool_per_participant':own/n,'units_full_pool_per_participant':full/n,
        'incremental_units_per_participant':(full-own)/n,
        'relative_capacity_lift':full/own-1 if own else None,
        'expected_fragmented_tickets_no_pool':fragments,'expected_residual_full_pool':residual,
        'expected_units_full_pool_if_one_per_person':sum(F(min(n,t//40))*p for (t,_,_),p in joint.items()),
        'badge_cap_status':'one_per_person_is_sensitivity_not_verified_policy'}


def partial_metrics(pmf,n,policy):
    """Explicit contributions; full units are theoretical, not inventory claims.

    own_first_surplus: donors keep their first 40, below-40 members retain all;
      only >40 surplus transfers. Recipient 0 tops up first, then remaining pot
      funds whole units. Other below-40 balances stay with their owners.
    keep10_remainders: everyone reserves all complete personal units and keeps
      up to ten remainder tickets for other prizes; only excess remainders pool.
    """
    check(pmf)
    if n<1 or policy not in ('own_first_surplus','keep10_remainders'): raise ValueError('Invalid partial policy')
    if policy=='keep10_remainders':
        contribution=lambda t:max(0,t%40-10)
    else:
        contribution=lambda t:max(0,t-40)
    other={(0,0):F(1)}
    for _ in range(n-1):
        nxt=defaultdict(F)
        for (pot,q),mass in other.items():
            for t,p in pmf.items(): nxt[(pot+contribution(t),q+int(t>=40))]+=mass*p
        other=dict(nxt)
    success=any_success=all_success=capacity=F(0)
    for t,p in pmf.items():
        for (pot,q),mass in other.items():
            probability=p*mass
            if policy=='own_first_surplus':
                pool=pot+contribution(t)
                target=int(t>=40)
                if not target and pool>=40-t:
                    target=1;pool-=40-t
                    extra_target=1
                else: extra_target=0
                units=q+int(t>=40)+extra_target+pool//40
                unique_capacity=q+int(t>=40)+extra_target+pool//40
            else:
                pool=pot+contribution(t)
                target=int(t>=40 or pool>=40)
                # Own units are accounted by linearity below; q is owners, not units.
                units=pool//40
                unique_capacity=q+int(t>=40)+pool//40
            success+=probability*target
            any_success+=probability*int(q>0 or t>=40 or units>0)
            all_success+=probability*int(unique_capacity>=n)
            capacity+=probability*units
    if policy=='keep10_remainders': capacity+=n*sum(F(t//40)*p for t,p in pmf.items())
    total=n*sum(F(t)*p for t,p in pmf.items())
    residual=total-40*capacity
    if residual<0: raise ValueError('Partial contributions created tickets')
    return {'policy':policy,'group_size':n,'p_prioritized_recipient_40':success,
            'p_at_least_one_qualifying_recipient':any_success,'p_capacity_for_everyone_under_protocol':all_success,
            'expected_potential_units':capacity,'units_per_participant':capacity/n,
            'expected_unspent_retained_and_residual_tickets':residual,
            'contribution_permission':'hypothetical_not_verified','nonrecipient_retained_tickets':'kept_for_owners_not_assumed_worthless'}


def allocate_two(tickets,allocation):
    return allocate_team(tickets,2,allocation)


def allocate_team(tickets,size,allocation):
    if type(tickets) is not int or tickets<0: raise ValueError('Integer team award required')
    if type(size) is not int or size<2: raise ValueError('Invalid team size')
    if allocation=='integer_equal':
        q,r=divmod(tickets,size)
        return tuple(q+int(i>=size-r) for i in range(size))
    if allocation=='prioritize_A': return (tickets,)+(0,)*(size-1)
    raise ValueError('Unsupported allocation')
