<template>
    <div>
        <section class="content-list-wrapper">
            <p-pane-layout class="content-wrapper">
                <h3 class="content-title">
                    {{ $t('IDENTITY.USER.NOTIFICATION.FORM.BASE_INFO') }}
                </h3>
                <add-notification-data :project-id="projectId"
                                       :supported-schema="supportedSchema"
                                       :protocol-type="protocolType"
                                       :protocol-id="protocolId"
                                       @change="onChangeData"
                />
            </p-pane-layout>
            <p-pane-layout class="content-wrapper">
                <h3 class="content-title">
                    {{ $t('IDENTITY.USER.NOTIFICATION.FORM.SCHEDULE') }}
                </h3>
                <h4 class="sub-title">
                    {{ $t('IDENTITY.USER.NOTIFICATION.FORM.SETTING_MODE') }}
                </h4>
                <add-notification-schedule @change="onChangeSchedule" />
            </p-pane-layout>
            <p-pane-layout class="content-wrapper">
                <h3 class="content-title">
                    {{ $t('IDENTITY.USER.NOTIFICATION.FORM.TOPIC') }}
                </h3>
                <h4 class="sub-title">
                    {{ $t('IDENTITY.USER.NOTIFICATION.FORM.SETTING_MODE') }}
                </h4>
                <add-notification-topic @change="onChangeTopic" />
            </p-pane-layout>
        </section>
        <div class="button-group">
            <p-button style-type="tertiary"
                      class="text-button"
                      @click="$router.go(-1)"
            >
                {{ $t('COMMON.TAGS.CANCEL') }}
            </p-button>
            <p-button style-type="primary"
                      class="text-button"
                      :disabled="!isDataValid || !isScheduleValid || !isTopicValid"
                      @click="onClickSave"
            >
                {{ $t('COMMON.TAGS.SAVE') }}
            </p-button>
        </div>
    </div>
</template>

<script lang="ts">
import {
    getCurrentInstance, reactive, toRefs,
} from 'vue';
import type { Vue } from 'vue/types/vue';

import {
    PButton, PPaneLayout,
} from '@spaceone/design-system';

import { SpaceConnector } from '@cloudforet/core-lib/space-connector';

import { i18n } from '@/translations';

import { showSuccessMessage } from '@/lib/helper/notice-alert-helper';

import ErrorHandler from '@/common/composables/error/errorHandler';

import AddNotificationSchedule from '@/services/notification/modules/AddNotificationSchedule.vue';
import AddNotificationTopic from '@/services/notification/modules/AddNotificationTopic.vue';
import AddNotificationData from '@/services/notification/notification-add/modules/AddNotificationData.vue';

interface NotificationSchedule {
    day_of_week: [],
    start_hour: number;
    end_hour: number;
}

export default {
    name: 'NotificationAddForm',
    components: {
        AddNotificationData,
        AddNotificationSchedule,
        AddNotificationTopic,
        PPaneLayout,
        PButton,
    },
    props: {
        userId: {
            type: String,
            default: '',
        },
        projectId: {
            type: String,
            default: '',
        },
        supportedSchema: {
            type: [String, Array],
            default: null,
        },
        protocolType: {
            type: String,
            default: '',
        },
        protocolId: {
            type: String,
            default: undefined,
        },
    },
    setup(props) {
        const vm = getCurrentInstance()?.proxy as Vue;
        const state = reactive({
            type: '',
            description: null,
            project: {} as any,
            //
            isDataValid: false,
            notificationLevel: 'LV1',
            //
            channelName: '',
            data: {},
            topicMode: false,
            topicList: [],
            isTopicValid: true,
            //
            schedule: null as NotificationSchedule | null,
            isScheduled: false,
            isScheduleValid: true,
        });

        const createUserChannel = async () => {
            try {
                await SpaceConnector.client.notification.userChannel.create({
                    protocol_id: props.protocolId,
                    name: state.channelName,
                    data: state.data,
                    schema: props.supportedSchema,
                    is_subscribe: state.topicMode,
                    subscriptions: state.topicList,
                    schedule: state.schedule,
                    is_scheduled: state.isScheduled,
                    user_id: props.userId,
                });
                showSuccessMessage(i18n.t('IDENTITY.USER.NOTIFICATION.FORM.ALT_S_CREATE_USER_CHANNEL'), '');
            } catch (e) {
                ErrorHandler.handleRequestError(e, i18n.t('IDENTITY.USER.NOTIFICATION.FORM.ALT_E_CREATE_USER_CHANNEL'));
            }
        };

        const createProjectChannel = async () => {
            try {
                await SpaceConnector.client.notification.projectChannel.create({
                    protocol_id: props.protocolId,
                    name: state.channelName,
                    data: state.data,
                    schema: props.supportedSchema,
                    is_subscribe: state.topicMode,
                    subscriptions: state.topicList,
                    schedule: state.schedule,
                    is_scheduled: state.isScheduled,
                    user_id: props.userId,
                    notification_level: state.notificationLevel,
                    project_id: props.projectId,
                });
                showSuccessMessage(i18n.t('IDENTITY.USER.NOTIFICATION.FORM.ALT_S_CREATE_PROJECT_CHANNEL'), '');
            } catch (e) {
                ErrorHandler.handleRequestError(e, i18n.t('IDENTITY.USER.NOTIFICATION.FORM.ALT_E_CREATE_PROJECT_CHANNEL'));
            }
        };

        const onClickSave = async () => {
            try {
                if (props.projectId) await createProjectChannel();
                else await createUserChannel();
                vm.$router.back();
            } catch (e) {
                ErrorHandler.handleError(e);
            }
        };

        const onChangeData = (value) => {
            state.channelName = value.channelName;
            state.data = value.data;
            state.notificationLevel = value.level;
            state.isDataValid = value.isValid;
        };

        const onChangeSchedule = (value) => {
            state.schedule = value.schedule;
            state.isScheduled = value.is_scheduled;
            state.isScheduleValid = value.isScheduleValid;
        };

        const onChangeTopic = (value) => {
            state.topicMode = value.topicMode;
            state.topicList = value.selectedTopic;
            state.isTopicValid = value.isTopicValid;
        };

        return {
            ...toRefs(state),
            onClickSave,
            onChangeData,
            onChangeSchedule,
            onChangeTopic,
        };
    },
};
</script>

<style lang="postcss" scoped>
.content-list-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1rem;
}
.button-group {
    display: flex;
    justify-content: flex-end;
    .text-button {
        margin-left: 1rem;
    }
}
.content-wrapper {
    padding: 2rem 1rem 3.5rem;
}
.content-title {
    font-size: 1.5rem;
    line-height: 135%;
}
.sub-title {
    @apply font-bold;
    font-size: 0.875rem;
    line-height: 140%;
    margin-top: 1.25rem;
    margin-bottom: 0.375rem;
}
</style>
