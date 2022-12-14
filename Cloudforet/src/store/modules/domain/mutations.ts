import type { DomainState } from './type';

export const setDomain = (state: DomainState, domainInfo: DomainState): void => {
    state.domainId = domainInfo.domainId;
    state.name = domainInfo.name;
    state.authOptions = domainInfo.authOptions;
    state.extendedAuthType = domainInfo.extendedAuthType;
};

export const setBillingEnabled = (state: DomainState, billingEnabled: boolean) => {
    state.billingEnabled = billingEnabled;
};
