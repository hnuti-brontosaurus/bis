import { emptySplitApi as api } from './emptyApi'
const injectedRtkApi = api.injectEndpoints({
  endpoints: build => ({
    authLoginCreate: build.mutation<
      AuthLoginCreateApiResponse,
      AuthLoginCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/auth/login/`,
        method: 'POST',
        body: queryArg.loginRequest,
      }),
    }),
    authLogoutCreate: build.mutation<
      AuthLogoutCreateApiResponse,
      AuthLogoutCreateApiArg
    >({
      query: () => ({ url: `/api/auth/logout/`, method: 'POST' }),
    }),
    authResetPasswordCreate: build.mutation<
      AuthResetPasswordCreateApiResponse,
      AuthResetPasswordCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/auth/reset_password/`,
        method: 'POST',
        body: queryArg.resetPasswordRequest,
      }),
    }),
    authSendVerificationLinkCreate: build.mutation<
      AuthSendVerificationLinkCreateApiResponse,
      AuthSendVerificationLinkCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/auth/send_verification_link/`,
        method: 'POST',
        body: queryArg.sendVerificationLinkRequest,
      }),
    }),
    authWhoamiRetrieve: build.query<
      AuthWhoamiRetrieveApiResponse,
      AuthWhoamiRetrieveApiArg
    >({
      query: () => ({ url: `/api/auth/whoami/` }),
    }),
    categoriesAdministrationUnitCategoriesList: build.query<
      CategoriesAdministrationUnitCategoriesListApiResponse,
      CategoriesAdministrationUnitCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/administration_unit_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesAdministrationUnitCategoriesRetrieve: build.query<
      CategoriesAdministrationUnitCategoriesRetrieveApiResponse,
      CategoriesAdministrationUnitCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/administration_unit_categories/${queryArg.id}/`,
      }),
    }),
    categoriesDietCategoriesList: build.query<
      CategoriesDietCategoriesListApiResponse,
      CategoriesDietCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/diet_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesDietCategoriesRetrieve: build.query<
      CategoriesDietCategoriesRetrieveApiResponse,
      CategoriesDietCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/diet_categories/${queryArg.id}/`,
      }),
    }),
    categoriesDonationSourceCategoriesList: build.query<
      CategoriesDonationSourceCategoriesListApiResponse,
      CategoriesDonationSourceCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/donation_source_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesDonationSourceCategoriesRetrieve: build.query<
      CategoriesDonationSourceCategoriesRetrieveApiResponse,
      CategoriesDonationSourceCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/donation_source_categories/${queryArg.id}/`,
      }),
    }),
    categoriesEventCategoriesList: build.query<
      CategoriesEventCategoriesListApiResponse,
      CategoriesEventCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesEventCategoriesRetrieve: build.query<
      CategoriesEventCategoriesRetrieveApiResponse,
      CategoriesEventCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_categories/${queryArg.id}/`,
      }),
    }),
    categoriesEventGroupCategoriesList: build.query<
      CategoriesEventGroupCategoriesListApiResponse,
      CategoriesEventGroupCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_group_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesEventGroupCategoriesRetrieve: build.query<
      CategoriesEventGroupCategoriesRetrieveApiResponse,
      CategoriesEventGroupCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_group_categories/${queryArg.id}/`,
      }),
    }),
    categoriesEventIntendedForCategoriesList: build.query<
      CategoriesEventIntendedForCategoriesListApiResponse,
      CategoriesEventIntendedForCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_intended_for_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesEventIntendedForCategoriesRetrieve: build.query<
      CategoriesEventIntendedForCategoriesRetrieveApiResponse,
      CategoriesEventIntendedForCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_intended_for_categories/${queryArg.id}/`,
      }),
    }),
    categoriesEventProgramCategoriesList: build.query<
      CategoriesEventProgramCategoriesListApiResponse,
      CategoriesEventProgramCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_program_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesEventProgramCategoriesRetrieve: build.query<
      CategoriesEventProgramCategoriesRetrieveApiResponse,
      CategoriesEventProgramCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/event_program_categories/${queryArg.id}/`,
      }),
    }),
    categoriesGrantCategoriesList: build.query<
      CategoriesGrantCategoriesListApiResponse,
      CategoriesGrantCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/grant_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesGrantCategoriesRetrieve: build.query<
      CategoriesGrantCategoriesRetrieveApiResponse,
      CategoriesGrantCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/grant_categories/${queryArg.id}/`,
      }),
    }),
    categoriesHealthInsuranceCompaniesList: build.query<
      CategoriesHealthInsuranceCompaniesListApiResponse,
      CategoriesHealthInsuranceCompaniesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/health_insurance_companies/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesHealthInsuranceCompaniesRetrieve: build.query<
      CategoriesHealthInsuranceCompaniesRetrieveApiResponse,
      CategoriesHealthInsuranceCompaniesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/health_insurance_companies/${queryArg.id}/`,
      }),
    }),
    categoriesLocationAccessibilityCategoriesList: build.query<
      CategoriesLocationAccessibilityCategoriesListApiResponse,
      CategoriesLocationAccessibilityCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/location_accessibility_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesLocationAccessibilityCategoriesRetrieve: build.query<
      CategoriesLocationAccessibilityCategoriesRetrieveApiResponse,
      CategoriesLocationAccessibilityCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/location_accessibility_categories/${queryArg.id}/`,
      }),
    }),
    categoriesLocationProgramCategoriesList: build.query<
      CategoriesLocationProgramCategoriesListApiResponse,
      CategoriesLocationProgramCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/location_program_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesLocationProgramCategoriesRetrieve: build.query<
      CategoriesLocationProgramCategoriesRetrieveApiResponse,
      CategoriesLocationProgramCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/location_program_categories/${queryArg.id}/`,
      }),
    }),
    categoriesMembershipCategoriesList: build.query<
      CategoriesMembershipCategoriesListApiResponse,
      CategoriesMembershipCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/membership_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesMembershipCategoriesRetrieve: build.query<
      CategoriesMembershipCategoriesRetrieveApiResponse,
      CategoriesMembershipCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/membership_categories/${queryArg.id}/`,
      }),
    }),
    categoriesOpportunityCategoriesList: build.query<
      CategoriesOpportunityCategoriesListApiResponse,
      CategoriesOpportunityCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/opportunity_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesOpportunityCategoriesRetrieve: build.query<
      CategoriesOpportunityCategoriesRetrieveApiResponse,
      CategoriesOpportunityCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/opportunity_categories/${queryArg.id}/`,
      }),
    }),
    categoriesOrganizerRoleCategoriesList: build.query<
      CategoriesOrganizerRoleCategoriesListApiResponse,
      CategoriesOrganizerRoleCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/organizer_role_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesOrganizerRoleCategoriesRetrieve: build.query<
      CategoriesOrganizerRoleCategoriesRetrieveApiResponse,
      CategoriesOrganizerRoleCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/organizer_role_categories/${queryArg.id}/`,
      }),
    }),
    categoriesPronounCategoriesList: build.query<
      CategoriesPronounCategoriesListApiResponse,
      CategoriesPronounCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/pronoun_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesPronounCategoriesRetrieve: build.query<
      CategoriesPronounCategoriesRetrieveApiResponse,
      CategoriesPronounCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/pronoun_categories/${queryArg.id}/`,
      }),
    }),
    categoriesQualificationCategoriesList: build.query<
      CategoriesQualificationCategoriesListApiResponse,
      CategoriesQualificationCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/qualification_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesQualificationCategoriesRetrieve: build.query<
      CategoriesQualificationCategoriesRetrieveApiResponse,
      CategoriesQualificationCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/qualification_categories/${queryArg.id}/`,
      }),
    }),
    categoriesRegionsList: build.query<
      CategoriesRegionsListApiResponse,
      CategoriesRegionsListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/regions/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesRegionsRetrieve: build.query<
      CategoriesRegionsRetrieveApiResponse,
      CategoriesRegionsRetrieveApiArg
    >({
      query: queryArg => ({ url: `/api/categories/regions/${queryArg.id}/` }),
    }),
    categoriesRoleCategoriesList: build.query<
      CategoriesRoleCategoriesListApiResponse,
      CategoriesRoleCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/role_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesRoleCategoriesRetrieve: build.query<
      CategoriesRoleCategoriesRetrieveApiResponse,
      CategoriesRoleCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/role_categories/${queryArg.id}/`,
      }),
    }),
    categoriesTeamRoleCategoriesList: build.query<
      CategoriesTeamRoleCategoriesListApiResponse,
      CategoriesTeamRoleCategoriesListApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/team_role_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    categoriesTeamRoleCategoriesRetrieve: build.query<
      CategoriesTeamRoleCategoriesRetrieveApiResponse,
      CategoriesTeamRoleCategoriesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/categories/team_role_categories/${queryArg.id}/`,
      }),
    }),
    frontendDashboardItemsList: build.query<
      FrontendDashboardItemsListApiResponse,
      FrontendDashboardItemsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/dashboard_items/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendDashboardItemsRetrieve: build.query<
      FrontendDashboardItemsRetrieveApiResponse,
      FrontendDashboardItemsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/dashboard_items/${queryArg.id}/`,
      }),
    }),
    frontendEventDraftsList: build.query<
      FrontendEventDraftsListApiResponse,
      FrontendEventDraftsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/event_drafts/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventDraftsCreate: build.mutation<
      FrontendEventDraftsCreateApiResponse,
      FrontendEventDraftsCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/event_drafts/`,
        method: 'POST',
        body: queryArg.eventDraft,
      }),
    }),
    frontendEventDraftsRetrieve: build.query<
      FrontendEventDraftsRetrieveApiResponse,
      FrontendEventDraftsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/event_drafts/${queryArg.id}/`,
      }),
    }),
    frontendEventDraftsUpdate: build.mutation<
      FrontendEventDraftsUpdateApiResponse,
      FrontendEventDraftsUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/event_drafts/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.eventDraft,
      }),
    }),
    frontendEventDraftsPartialUpdate: build.mutation<
      FrontendEventDraftsPartialUpdateApiResponse,
      FrontendEventDraftsPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/event_drafts/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedEventDraft,
      }),
    }),
    frontendEventDraftsDestroy: build.mutation<
      FrontendEventDraftsDestroyApiResponse,
      FrontendEventDraftsDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/event_drafts/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendEventsList: build.query<
      FrontendEventsListApiResponse,
      FrontendEventsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsCreate: build.mutation<
      FrontendEventsCreateApiResponse,
      FrontendEventsCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/`,
        method: 'POST',
        body: queryArg.event,
      }),
    }),
    frontendEventsFinanceReceiptsList: build.query<
      FrontendEventsFinanceReceiptsListApiResponse,
      FrontendEventsFinanceReceiptsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/finance/receipts/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsFinanceReceiptsCreate: build.mutation<
      FrontendEventsFinanceReceiptsCreateApiResponse,
      FrontendEventsFinanceReceiptsCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/finance/receipts/`,
        method: 'POST',
        body: queryArg.financeReceipt,
      }),
    }),
    frontendEventsFinanceReceiptsRetrieve: build.query<
      FrontendEventsFinanceReceiptsRetrieveApiResponse,
      FrontendEventsFinanceReceiptsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/finance/receipts/${queryArg.id}/`,
      }),
    }),
    frontendEventsFinanceReceiptsUpdate: build.mutation<
      FrontendEventsFinanceReceiptsUpdateApiResponse,
      FrontendEventsFinanceReceiptsUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/finance/receipts/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.financeReceipt,
      }),
    }),
    frontendEventsFinanceReceiptsPartialUpdate: build.mutation<
      FrontendEventsFinanceReceiptsPartialUpdateApiResponse,
      FrontendEventsFinanceReceiptsPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/finance/receipts/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedFinanceReceipt,
      }),
    }),
    frontendEventsFinanceReceiptsDestroy: build.mutation<
      FrontendEventsFinanceReceiptsDestroyApiResponse,
      FrontendEventsFinanceReceiptsDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/finance/receipts/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendEventsGetAttendanceListRetrieve: build.query<
      FrontendEventsGetAttendanceListRetrieveApiResponse,
      FrontendEventsGetAttendanceListRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/get_attendance_list/`,
        params: { formatting: queryArg.formatting },
      }),
    }),
    frontendEventsGetParticipantsListRetrieve: build.query<
      FrontendEventsGetParticipantsListRetrieveApiResponse,
      FrontendEventsGetParticipantsListRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/get_participants_list/`,
      }),
    }),
    frontendEventsOrganizersList: build.query<
      FrontendEventsOrganizersListApiResponse,
      FrontendEventsOrganizersListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/organizers/`,
        params: {
          _search_id: queryArg._search_id,
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsOrganizersRetrieve: build.query<
      FrontendEventsOrganizersRetrieveApiResponse,
      FrontendEventsOrganizersRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/organizers/${queryArg.id}/`,
      }),
    }),
    frontendEventsPropagationImagesList: build.query<
      FrontendEventsPropagationImagesListApiResponse,
      FrontendEventsPropagationImagesListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/propagation/images/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsPropagationImagesCreate: build.mutation<
      FrontendEventsPropagationImagesCreateApiResponse,
      FrontendEventsPropagationImagesCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/propagation/images/`,
        method: 'POST',
        body: queryArg.eventPropagationImage,
      }),
    }),
    frontendEventsPropagationImagesRetrieve: build.query<
      FrontendEventsPropagationImagesRetrieveApiResponse,
      FrontendEventsPropagationImagesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/propagation/images/${queryArg.id}/`,
      }),
    }),
    frontendEventsPropagationImagesUpdate: build.mutation<
      FrontendEventsPropagationImagesUpdateApiResponse,
      FrontendEventsPropagationImagesUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/propagation/images/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.eventPropagationImage,
      }),
    }),
    frontendEventsPropagationImagesPartialUpdate: build.mutation<
      FrontendEventsPropagationImagesPartialUpdateApiResponse,
      FrontendEventsPropagationImagesPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/propagation/images/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedEventPropagationImage,
      }),
    }),
    frontendEventsPropagationImagesDestroy: build.mutation<
      FrontendEventsPropagationImagesDestroyApiResponse,
      FrontendEventsPropagationImagesDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/propagation/images/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendEventsRecordAttendanceListPagesList: build.query<
      FrontendEventsRecordAttendanceListPagesListApiResponse,
      FrontendEventsRecordAttendanceListPagesListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/attendance_list_pages/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsRecordAttendanceListPagesCreate: build.mutation<
      FrontendEventsRecordAttendanceListPagesCreateApiResponse,
      FrontendEventsRecordAttendanceListPagesCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/attendance_list_pages/`,
        method: 'POST',
        body: queryArg.attendanceListPage,
      }),
    }),
    frontendEventsRecordAttendanceListPagesRetrieve: build.query<
      FrontendEventsRecordAttendanceListPagesRetrieveApiResponse,
      FrontendEventsRecordAttendanceListPagesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/attendance_list_pages/${queryArg.id}/`,
      }),
    }),
    frontendEventsRecordAttendanceListPagesUpdate: build.mutation<
      FrontendEventsRecordAttendanceListPagesUpdateApiResponse,
      FrontendEventsRecordAttendanceListPagesUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/attendance_list_pages/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.attendanceListPage,
      }),
    }),
    frontendEventsRecordAttendanceListPagesPartialUpdate: build.mutation<
      FrontendEventsRecordAttendanceListPagesPartialUpdateApiResponse,
      FrontendEventsRecordAttendanceListPagesPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/attendance_list_pages/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedAttendanceListPage,
      }),
    }),
    frontendEventsRecordAttendanceListPagesDestroy: build.mutation<
      FrontendEventsRecordAttendanceListPagesDestroyApiResponse,
      FrontendEventsRecordAttendanceListPagesDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/attendance_list_pages/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendEventsRecordParticipantsList: build.query<
      FrontendEventsRecordParticipantsListApiResponse,
      FrontendEventsRecordParticipantsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/participants/`,
        params: {
          _search_id: queryArg._search_id,
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsRecordParticipantsRetrieve: build.query<
      FrontendEventsRecordParticipantsRetrieveApiResponse,
      FrontendEventsRecordParticipantsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/participants/${queryArg.id}/`,
      }),
    }),
    frontendEventsRecordPhotosList: build.query<
      FrontendEventsRecordPhotosListApiResponse,
      FrontendEventsRecordPhotosListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/photos/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsRecordPhotosCreate: build.mutation<
      FrontendEventsRecordPhotosCreateApiResponse,
      FrontendEventsRecordPhotosCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/photos/`,
        method: 'POST',
        body: queryArg.eventPhoto,
      }),
    }),
    frontendEventsRecordPhotosRetrieve: build.query<
      FrontendEventsRecordPhotosRetrieveApiResponse,
      FrontendEventsRecordPhotosRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/photos/${queryArg.id}/`,
      }),
    }),
    frontendEventsRecordPhotosUpdate: build.mutation<
      FrontendEventsRecordPhotosUpdateApiResponse,
      FrontendEventsRecordPhotosUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/photos/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.eventPhoto,
      }),
    }),
    frontendEventsRecordPhotosPartialUpdate: build.mutation<
      FrontendEventsRecordPhotosPartialUpdateApiResponse,
      FrontendEventsRecordPhotosPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/photos/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedEventPhoto,
      }),
    }),
    frontendEventsRecordPhotosDestroy: build.mutation<
      FrontendEventsRecordPhotosDestroyApiResponse,
      FrontendEventsRecordPhotosDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/record/photos/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendEventsRegisteredList: build.query<
      FrontendEventsRegisteredListApiResponse,
      FrontendEventsRegisteredListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registered/`,
        params: {
          _search_id: queryArg._search_id,
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsRegisteredRetrieve: build.query<
      FrontendEventsRegisteredRetrieveApiResponse,
      FrontendEventsRegisteredRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registered/${queryArg.id}/`,
      }),
    }),
    frontendEventsRegistrationApplicationsList: build.query<
      FrontendEventsRegistrationApplicationsListApiResponse,
      FrontendEventsRegistrationApplicationsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/applications/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsRegistrationApplicationsCreate: build.mutation<
      FrontendEventsRegistrationApplicationsCreateApiResponse,
      FrontendEventsRegistrationApplicationsCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/applications/`,
        method: 'POST',
        body: queryArg.eventApplication,
      }),
    }),
    frontendEventsRegistrationApplicationsRetrieve: build.query<
      FrontendEventsRegistrationApplicationsRetrieveApiResponse,
      FrontendEventsRegistrationApplicationsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/applications/${queryArg.id}/`,
      }),
    }),
    frontendEventsRegistrationApplicationsUpdate: build.mutation<
      FrontendEventsRegistrationApplicationsUpdateApiResponse,
      FrontendEventsRegistrationApplicationsUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/applications/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.eventApplication,
      }),
    }),
    frontendEventsRegistrationApplicationsPartialUpdate: build.mutation<
      FrontendEventsRegistrationApplicationsPartialUpdateApiResponse,
      FrontendEventsRegistrationApplicationsPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/applications/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedEventApplication,
      }),
    }),
    frontendEventsRegistrationApplicationsDestroy: build.mutation<
      FrontendEventsRegistrationApplicationsDestroyApiResponse,
      FrontendEventsRegistrationApplicationsDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/applications/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendEventsRegistrationQuestionnaireQuestionsList: build.query<
      FrontendEventsRegistrationQuestionnaireQuestionsListApiResponse,
      FrontendEventsRegistrationQuestionnaireQuestionsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/questionnaire/questions/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendEventsRegistrationQuestionnaireQuestionsCreate: build.mutation<
      FrontendEventsRegistrationQuestionnaireQuestionsCreateApiResponse,
      FrontendEventsRegistrationQuestionnaireQuestionsCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/questionnaire/questions/`,
        method: 'POST',
        body: queryArg.question,
      }),
    }),
    frontendEventsRegistrationQuestionnaireQuestionsRetrieve: build.query<
      FrontendEventsRegistrationQuestionnaireQuestionsRetrieveApiResponse,
      FrontendEventsRegistrationQuestionnaireQuestionsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/questionnaire/questions/${queryArg.id}/`,
      }),
    }),
    frontendEventsRegistrationQuestionnaireQuestionsUpdate: build.mutation<
      FrontendEventsRegistrationQuestionnaireQuestionsUpdateApiResponse,
      FrontendEventsRegistrationQuestionnaireQuestionsUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/questionnaire/questions/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.question,
      }),
    }),
    frontendEventsRegistrationQuestionnaireQuestionsPartialUpdate:
      build.mutation<
        FrontendEventsRegistrationQuestionnaireQuestionsPartialUpdateApiResponse,
        FrontendEventsRegistrationQuestionnaireQuestionsPartialUpdateApiArg
      >({
        query: queryArg => ({
          url: `/api/frontend/events/${queryArg.eventId}/registration/questionnaire/questions/${queryArg.id}/`,
          method: 'PATCH',
          body: queryArg.patchedQuestion,
        }),
      }),
    frontendEventsRegistrationQuestionnaireQuestionsDestroy: build.mutation<
      FrontendEventsRegistrationQuestionnaireQuestionsDestroyApiResponse,
      FrontendEventsRegistrationQuestionnaireQuestionsDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.eventId}/registration/questionnaire/questions/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendEventsRetrieve: build.query<
      FrontendEventsRetrieveApiResponse,
      FrontendEventsRetrieveApiArg
    >({
      query: queryArg => ({ url: `/api/frontend/events/${queryArg.id}/` }),
    }),
    frontendEventsUpdate: build.mutation<
      FrontendEventsUpdateApiResponse,
      FrontendEventsUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.event,
      }),
    }),
    frontendEventsPartialUpdate: build.mutation<
      FrontendEventsPartialUpdateApiResponse,
      FrontendEventsPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedEvent,
      }),
    }),
    frontendEventsDestroy: build.mutation<
      FrontendEventsDestroyApiResponse,
      FrontendEventsDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/events/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendGetUnknownUserRetrieve: build.query<
      FrontendGetUnknownUserRetrieveApiResponse,
      FrontendGetUnknownUserRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/get_unknown_user/`,
        params: {
          birthday: queryArg.birthday,
          first_name: queryArg.firstName,
          last_name: queryArg.lastName,
        },
      }),
    }),
    frontendLocationsList: build.query<
      FrontendLocationsListApiResponse,
      FrontendLocationsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/locations/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendLocationsCreate: build.mutation<
      FrontendLocationsCreateApiResponse,
      FrontendLocationsCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/locations/`,
        method: 'POST',
        body: queryArg.location,
      }),
    }),
    frontendLocationsRetrieve: build.query<
      FrontendLocationsRetrieveApiResponse,
      FrontendLocationsRetrieveApiArg
    >({
      query: queryArg => ({ url: `/api/frontend/locations/${queryArg.id}/` }),
    }),
    frontendLocationsUpdate: build.mutation<
      FrontendLocationsUpdateApiResponse,
      FrontendLocationsUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/locations/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.location,
      }),
    }),
    frontendLocationsPartialUpdate: build.mutation<
      FrontendLocationsPartialUpdateApiResponse,
      FrontendLocationsPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/locations/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedLocation,
      }),
    }),
    frontendLocationsDestroy: build.mutation<
      FrontendLocationsDestroyApiResponse,
      FrontendLocationsDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/locations/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendSearchUsersList: build.query<
      FrontendSearchUsersListApiResponse,
      FrontendSearchUsersListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/search_users/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendUsersList: build.query<
      FrontendUsersListApiResponse,
      FrontendUsersListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/`,
        params: {
          _search_id: queryArg._search_id,
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendUsersCreate: build.mutation<
      FrontendUsersCreateApiResponse,
      FrontendUsersCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/`,
        method: 'POST',
        body: queryArg.user,
      }),
    }),
    frontendUsersRetrieve: build.query<
      FrontendUsersRetrieveApiResponse,
      FrontendUsersRetrieveApiArg
    >({
      query: queryArg => ({ url: `/api/frontend/users/${queryArg.id}/` }),
    }),
    frontendUsersUpdate: build.mutation<
      FrontendUsersUpdateApiResponse,
      FrontendUsersUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.user,
      }),
    }),
    frontendUsersPartialUpdate: build.mutation<
      FrontendUsersPartialUpdateApiResponse,
      FrontendUsersPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedUser,
      }),
    }),
    frontendUsersDestroy: build.mutation<
      FrontendUsersDestroyApiResponse,
      FrontendUsersDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendUsersEventsWhereWasOrganizerList: build.query<
      FrontendUsersEventsWhereWasOrganizerListApiResponse,
      FrontendUsersEventsWhereWasOrganizerListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/events_where_was_organizer/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendUsersEventsWhereWasOrganizerRetrieve: build.query<
      FrontendUsersEventsWhereWasOrganizerRetrieveApiResponse,
      FrontendUsersEventsWhereWasOrganizerRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/events_where_was_organizer/${queryArg.id}/`,
      }),
    }),
    frontendUsersOpportunitiesList: build.query<
      FrontendUsersOpportunitiesListApiResponse,
      FrontendUsersOpportunitiesListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/opportunities/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendUsersOpportunitiesCreate: build.mutation<
      FrontendUsersOpportunitiesCreateApiResponse,
      FrontendUsersOpportunitiesCreateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/opportunities/`,
        method: 'POST',
        body: queryArg.opportunity,
      }),
    }),
    frontendUsersOpportunitiesRetrieve: build.query<
      FrontendUsersOpportunitiesRetrieveApiResponse,
      FrontendUsersOpportunitiesRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/opportunities/${queryArg.id}/`,
      }),
    }),
    frontendUsersOpportunitiesUpdate: build.mutation<
      FrontendUsersOpportunitiesUpdateApiResponse,
      FrontendUsersOpportunitiesUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/opportunities/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.opportunity,
      }),
    }),
    frontendUsersOpportunitiesPartialUpdate: build.mutation<
      FrontendUsersOpportunitiesPartialUpdateApiResponse,
      FrontendUsersOpportunitiesPartialUpdateApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/opportunities/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedOpportunity,
      }),
    }),
    frontendUsersOpportunitiesDestroy: build.mutation<
      FrontendUsersOpportunitiesDestroyApiResponse,
      FrontendUsersOpportunitiesDestroyApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/opportunities/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    frontendUsersParticipatedInEventsList: build.query<
      FrontendUsersParticipatedInEventsListApiResponse,
      FrontendUsersParticipatedInEventsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/participated_in_events/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendUsersParticipatedInEventsRetrieve: build.query<
      FrontendUsersParticipatedInEventsRetrieveApiResponse,
      FrontendUsersParticipatedInEventsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/participated_in_events/${queryArg.id}/`,
      }),
    }),
    frontendUsersRegisteredInEventsList: build.query<
      FrontendUsersRegisteredInEventsListApiResponse,
      FrontendUsersRegisteredInEventsListApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/registered_in_events/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    frontendUsersRegisteredInEventsRetrieve: build.query<
      FrontendUsersRegisteredInEventsRetrieveApiResponse,
      FrontendUsersRegisteredInEventsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/frontend/users/${queryArg.userId}/registered_in_events/${queryArg.id}/`,
      }),
    }),
    webAdministrationUnitsList: build.query<
      WebAdministrationUnitsListApiResponse,
      WebAdministrationUnitsListApiArg
    >({
      query: queryArg => ({
        url: `/api/web/administration_units/`,
        params: {
          category: queryArg.category,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    webAdministrationUnitsRetrieve: build.query<
      WebAdministrationUnitsRetrieveApiResponse,
      WebAdministrationUnitsRetrieveApiArg
    >({
      query: queryArg => ({
        url: `/api/web/administration_units/${queryArg.id}/`,
      }),
    }),
    webEventsList: build.query<WebEventsListApiResponse, WebEventsListApiArg>({
      query: queryArg => ({
        url: `/api/web/events/`,
        params: {
          administration_unit: queryArg.administrationUnit,
          category: queryArg.category,
          duration: queryArg.duration,
          duration__gte: queryArg.durationGte,
          duration__lte: queryArg.durationLte,
          end__gte: queryArg.endGte,
          end__lte: queryArg.endLte,
          group: queryArg.group,
          intended_for: queryArg.intendedFor,
          ordering: queryArg.ordering,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          program: queryArg.program,
          search: queryArg.search,
          start__gte: queryArg.startGte,
          start__lte: queryArg.startLte,
        },
      }),
    }),
    webEventsRetrieve: build.query<
      WebEventsRetrieveApiResponse,
      WebEventsRetrieveApiArg
    >({
      query: queryArg => ({ url: `/api/web/events/${queryArg.id}/` }),
    }),
    webOpportunitiesList: build.query<
      WebOpportunitiesListApiResponse,
      WebOpportunitiesListApiArg
    >({
      query: queryArg => ({
        url: `/api/web/opportunities/`,
        params: {
          category: queryArg.category,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    webOpportunitiesRetrieve: build.query<
      WebOpportunitiesRetrieveApiResponse,
      WebOpportunitiesRetrieveApiArg
    >({
      query: queryArg => ({ url: `/api/web/opportunities/${queryArg.id}/` }),
    }),
  }),
  overrideExisting: false,
})
export { injectedRtkApi as testApi }
export type AuthLoginCreateApiResponse = /** status 200  */ TokenResponse
export type AuthLoginCreateApiArg = {
  loginRequest: LoginRequest
}
export type AuthLogoutCreateApiResponse = unknown
export type AuthLogoutCreateApiArg = void
export type AuthResetPasswordCreateApiResponse =
  /** status 200  */ TokenResponse
export type AuthResetPasswordCreateApiArg = {
  resetPasswordRequest: ResetPasswordRequest
}
export type AuthSendVerificationLinkCreateApiResponse = unknown
export type AuthSendVerificationLinkCreateApiArg = {
  sendVerificationLinkRequest: SendVerificationLinkRequest
}
export type AuthWhoamiRetrieveApiResponse = /** status 200  */ UserIdResponse
export type AuthWhoamiRetrieveApiArg = void
export type CategoriesAdministrationUnitCategoriesListApiResponse =
  /** status 200  */ PaginatedAdministrationUnitCategoryList
export type CategoriesAdministrationUnitCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesAdministrationUnitCategoriesRetrieveApiResponse =
  /** status 200  */ AdministrationUnitCategory
export type CategoriesAdministrationUnitCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Typ organizační jednotky. */
  id: number
}
export type CategoriesDietCategoriesListApiResponse =
  /** status 200  */ PaginatedDietCategoryList
export type CategoriesDietCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesDietCategoriesRetrieveApiResponse =
  /** status 200  */ DietCategory
export type CategoriesDietCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Typ stravy. */
  id: number
}
export type CategoriesDonationSourceCategoriesListApiResponse =
  /** status 200  */ PaginatedDonationSourceCategoryList
export type CategoriesDonationSourceCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesDonationSourceCategoriesRetrieveApiResponse =
  /** status 200  */ DonationSourceCategory
export type CategoriesDonationSourceCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Zdroj dotace. */
  id: number
}
export type CategoriesEventCategoriesListApiResponse =
  /** status 200  */ PaginatedEventCategoryList
export type CategoriesEventCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesEventCategoriesRetrieveApiResponse =
  /** status 200  */ EventCategory
export type CategoriesEventCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Typ akce. */
  id: number
}
export type CategoriesEventGroupCategoriesListApiResponse =
  /** status 200  */ PaginatedEventGroupCategoryList
export type CategoriesEventGroupCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesEventGroupCategoriesRetrieveApiResponse =
  /** status 200  */ EventGroupCategory
export type CategoriesEventGroupCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Druh akce. */
  id: number
}
export type CategoriesEventIntendedForCategoriesListApiResponse =
  /** status 200  */ PaginatedEventIntendedForCategoryList
export type CategoriesEventIntendedForCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesEventIntendedForCategoriesRetrieveApiResponse =
  /** status 200  */ EventIntendedForCategory
export type CategoriesEventIntendedForCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Kategorie zaměření propagace. */
  id: number
}
export type CategoriesEventProgramCategoriesListApiResponse =
  /** status 200  */ PaginatedEventProgramCategoryList
export type CategoriesEventProgramCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesEventProgramCategoriesRetrieveApiResponse =
  /** status 200  */ EventProgramCategory
export type CategoriesEventProgramCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Program akce. */
  id: number
}
export type CategoriesGrantCategoriesListApiResponse =
  /** status 200  */ PaginatedGrantCategoryList
export type CategoriesGrantCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesGrantCategoriesRetrieveApiResponse =
  /** status 200  */ GrantCategory
export type CategoriesGrantCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Typ grantu. */
  id: number
}
export type CategoriesHealthInsuranceCompaniesListApiResponse =
  /** status 200  */ PaginatedHealthInsuranceCompanyList
export type CategoriesHealthInsuranceCompaniesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesHealthInsuranceCompaniesRetrieveApiResponse =
  /** status 200  */ HealthInsuranceCompany
export type CategoriesHealthInsuranceCompaniesRetrieveApiArg = {
  /** A unique integer value identifying this Zdravotní pojišťovna. */
  id: number
}
export type CategoriesLocationAccessibilityCategoriesListApiResponse =
  /** status 200  */ PaginatedLocationAccessibilityCategoryList
export type CategoriesLocationAccessibilityCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesLocationAccessibilityCategoriesRetrieveApiResponse =
  /** status 200  */ LocationAccessibilityCategory
export type CategoriesLocationAccessibilityCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Dostupnost lokality. */
  id: number
}
export type CategoriesLocationProgramCategoriesListApiResponse =
  /** status 200  */ PaginatedLocationProgramCategoryList
export type CategoriesLocationProgramCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesLocationProgramCategoriesRetrieveApiResponse =
  /** status 200  */ LocationProgramCategory
export type CategoriesLocationProgramCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Program lokality. */
  id: number
}
export type CategoriesMembershipCategoriesListApiResponse =
  /** status 200  */ PaginatedMembershipCategoryList
export type CategoriesMembershipCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesMembershipCategoriesRetrieveApiResponse =
  /** status 200  */ MembershipCategory
export type CategoriesMembershipCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Členství. */
  id: number
}
export type CategoriesOpportunityCategoriesListApiResponse =
  /** status 200  */ PaginatedOpportunityCategoryList
export type CategoriesOpportunityCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesOpportunityCategoriesRetrieveApiResponse =
  /** status 200  */ OpportunityCategory
export type CategoriesOpportunityCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Kagegorie příležitosti. */
  id: number
}
export type CategoriesOrganizerRoleCategoriesListApiResponse =
  /** status 200  */ PaginatedOrganizerRoleCategoryList
export type CategoriesOrganizerRoleCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesOrganizerRoleCategoriesRetrieveApiResponse =
  /** status 200  */ OrganizerRoleCategory
export type CategoriesOrganizerRoleCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Organizátorská role. */
  id: number
}
export type CategoriesPronounCategoriesListApiResponse =
  /** status 200  */ PaginatedPronounCategoryList
export type CategoriesPronounCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesPronounCategoriesRetrieveApiResponse =
  /** status 200  */ PronounCategory
export type CategoriesPronounCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Oslovení. */
  id: number
}
export type CategoriesQualificationCategoriesListApiResponse =
  /** status 200  */ PaginatedQualificationCategoryList
export type CategoriesQualificationCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesQualificationCategoriesRetrieveApiResponse =
  /** status 200  */ QualificationCategory
export type CategoriesQualificationCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Typ kvalifikace. */
  id: number
}
export type CategoriesRegionsListApiResponse =
  /** status 200  */ PaginatedRegionList
export type CategoriesRegionsListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesRegionsRetrieveApiResponse = /** status 200  */ Region
export type CategoriesRegionsRetrieveApiArg = {
  /** A unique integer value identifying this Kraj. */
  id: number
}
export type CategoriesRoleCategoriesListApiResponse =
  /** status 200  */ PaginatedRoleCategoryList
export type CategoriesRoleCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesRoleCategoriesRetrieveApiResponse =
  /** status 200  */ RoleCategory
export type CategoriesRoleCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Typ role. */
  id: number
}
export type CategoriesTeamRoleCategoriesListApiResponse =
  /** status 200  */ PaginatedTeamRoleCategoryList
export type CategoriesTeamRoleCategoriesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type CategoriesTeamRoleCategoriesRetrieveApiResponse =
  /** status 200  */ TeamRoleCategory
export type CategoriesTeamRoleCategoriesRetrieveApiArg = {
  /** A unique integer value identifying this Týmová role. */
  id: number
}
export type FrontendDashboardItemsListApiResponse =
  /** status 200  */ PaginatedDashboardItemList
export type FrontendDashboardItemsListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendDashboardItemsRetrieveApiResponse =
  /** status 200  */ DashboardItem
export type FrontendDashboardItemsRetrieveApiArg = {
  id: string
}
export type FrontendEventDraftsListApiResponse =
  /** status 200  */ PaginatedEventDraftList
export type FrontendEventDraftsListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventDraftsCreateApiResponse = /** status 201  */ EventDraft
export type FrontendEventDraftsCreateApiArg = {
  eventDraft: EventDraft
}
export type FrontendEventDraftsRetrieveApiResponse =
  /** status 200  */ EventDraft
export type FrontendEventDraftsRetrieveApiArg = {
  /** A unique integer value identifying this event draft. */
  id: number
}
export type FrontendEventDraftsUpdateApiResponse = /** status 200  */ EventDraft
export type FrontendEventDraftsUpdateApiArg = {
  /** A unique integer value identifying this event draft. */
  id: number
  eventDraft: EventDraft
}
export type FrontendEventDraftsPartialUpdateApiResponse =
  /** status 200  */ EventDraft
export type FrontendEventDraftsPartialUpdateApiArg = {
  /** A unique integer value identifying this event draft. */
  id: number
  patchedEventDraft: PatchedEventDraft
}
export type FrontendEventDraftsDestroyApiResponse = unknown
export type FrontendEventDraftsDestroyApiArg = {
  /** A unique integer value identifying this event draft. */
  id: number
}
export type FrontendEventsListApiResponse =
  /** status 200  */ PaginatedEventList
export type FrontendEventsListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  id?: number[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsCreateApiResponse = /** status 201  */ Event
export type FrontendEventsCreateApiArg = {
  event: Event
}
export type FrontendEventsFinanceReceiptsListApiResponse =
  /** status 200  */ PaginatedFinanceReceiptList
export type FrontendEventsFinanceReceiptsListApiArg = {
  eventId: string
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsFinanceReceiptsCreateApiResponse =
  /** status 201  */ FinanceReceipt
export type FrontendEventsFinanceReceiptsCreateApiArg = {
  eventId: string
  financeReceipt: FinanceReceipt
}
export type FrontendEventsFinanceReceiptsRetrieveApiResponse =
  /** status 200  */ FinanceReceipt
export type FrontendEventsFinanceReceiptsRetrieveApiArg = {
  eventId: string
  /** A unique integer value identifying this Účtenka. */
  id: number
}
export type FrontendEventsFinanceReceiptsUpdateApiResponse =
  /** status 200  */ FinanceReceipt
export type FrontendEventsFinanceReceiptsUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Účtenka. */
  id: number
  financeReceipt: FinanceReceipt
}
export type FrontendEventsFinanceReceiptsPartialUpdateApiResponse =
  /** status 200  */ FinanceReceipt
export type FrontendEventsFinanceReceiptsPartialUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Účtenka. */
  id: number
  patchedFinanceReceipt: PatchedFinanceReceipt
}
export type FrontendEventsFinanceReceiptsDestroyApiResponse = unknown
export type FrontendEventsFinanceReceiptsDestroyApiArg = {
  eventId: string
  /** A unique integer value identifying this Účtenka. */
  id: number
}
export type FrontendEventsGetAttendanceListRetrieveApiResponse = unknown
export type FrontendEventsGetAttendanceListRetrieveApiArg = {
  eventId: number
  /** * `pdf` - pdf
   * `xlsx` - xlsx */
  formatting?: 'pdf' | 'xlsx'
}
export type FrontendEventsGetParticipantsListRetrieveApiResponse = unknown
export type FrontendEventsGetParticipantsListRetrieveApiArg = {
  eventId: number
}
export type FrontendEventsOrganizersListApiResponse =
  /** status 200  */ PaginatedUserList
export type FrontendEventsOrganizersListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  _search_id?: string[]
  eventId: string
  /** Více hodnot lze oddělit čárkami. */
  id?: string[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsOrganizersRetrieveApiResponse =
  /** status 200  */ User
export type FrontendEventsOrganizersRetrieveApiArg = {
  eventId: string
  /** A UUID string identifying this Uživatel. */
  id: string
}
export type FrontendEventsPropagationImagesListApiResponse =
  /** status 200  */ PaginatedEventPropagationImageList
export type FrontendEventsPropagationImagesListApiArg = {
  eventId: string
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsPropagationImagesCreateApiResponse =
  /** status 201  */ EventPropagationImage
export type FrontendEventsPropagationImagesCreateApiArg = {
  eventId: string
  eventPropagationImage: EventPropagationImage
}
export type FrontendEventsPropagationImagesRetrieveApiResponse =
  /** status 200  */ EventPropagationImage
export type FrontendEventsPropagationImagesRetrieveApiArg = {
  eventId: string
  /** A unique integer value identifying this Obrázek k propagaci. */
  id: number
}
export type FrontendEventsPropagationImagesUpdateApiResponse =
  /** status 200  */ EventPropagationImage
export type FrontendEventsPropagationImagesUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Obrázek k propagaci. */
  id: number
  eventPropagationImage: EventPropagationImage
}
export type FrontendEventsPropagationImagesPartialUpdateApiResponse =
  /** status 200  */ EventPropagationImage
export type FrontendEventsPropagationImagesPartialUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Obrázek k propagaci. */
  id: number
  patchedEventPropagationImage: PatchedEventPropagationImage
}
export type FrontendEventsPropagationImagesDestroyApiResponse = unknown
export type FrontendEventsPropagationImagesDestroyApiArg = {
  eventId: string
  /** A unique integer value identifying this Obrázek k propagaci. */
  id: number
}
export type FrontendEventsRecordAttendanceListPagesListApiResponse =
  /** status 200  */ PaginatedAttendanceListPageList
export type FrontendEventsRecordAttendanceListPagesListApiArg = {
  eventId: string
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsRecordAttendanceListPagesCreateApiResponse =
  /** status 201  */ AttendanceListPage
export type FrontendEventsRecordAttendanceListPagesCreateApiArg = {
  eventId: string
  attendanceListPage: AttendanceListPage
}
export type FrontendEventsRecordAttendanceListPagesRetrieveApiResponse =
  /** status 200  */ AttendanceListPage
export type FrontendEventsRecordAttendanceListPagesRetrieveApiArg = {
  eventId: string
  /** A unique integer value identifying this Prezenční listina. */
  id: number
}
export type FrontendEventsRecordAttendanceListPagesUpdateApiResponse =
  /** status 200  */ AttendanceListPage
export type FrontendEventsRecordAttendanceListPagesUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Prezenční listina. */
  id: number
  attendanceListPage: AttendanceListPage
}
export type FrontendEventsRecordAttendanceListPagesPartialUpdateApiResponse =
  /** status 200  */ AttendanceListPage
export type FrontendEventsRecordAttendanceListPagesPartialUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Prezenční listina. */
  id: number
  patchedAttendanceListPage: PatchedAttendanceListPage
}
export type FrontendEventsRecordAttendanceListPagesDestroyApiResponse = unknown
export type FrontendEventsRecordAttendanceListPagesDestroyApiArg = {
  eventId: string
  /** A unique integer value identifying this Prezenční listina. */
  id: number
}
export type FrontendEventsRecordParticipantsListApiResponse =
  /** status 200  */ PaginatedUserList
export type FrontendEventsRecordParticipantsListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  _search_id?: string[]
  eventId: string
  /** Více hodnot lze oddělit čárkami. */
  id?: string[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsRecordParticipantsRetrieveApiResponse =
  /** status 200  */ User
export type FrontendEventsRecordParticipantsRetrieveApiArg = {
  eventId: string
  /** A UUID string identifying this Uživatel. */
  id: string
}
export type FrontendEventsRecordPhotosListApiResponse =
  /** status 200  */ PaginatedEventPhotoList
export type FrontendEventsRecordPhotosListApiArg = {
  eventId: string
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsRecordPhotosCreateApiResponse =
  /** status 201  */ EventPhoto
export type FrontendEventsRecordPhotosCreateApiArg = {
  eventId: string
  eventPhoto: EventPhoto
}
export type FrontendEventsRecordPhotosRetrieveApiResponse =
  /** status 200  */ EventPhoto
export type FrontendEventsRecordPhotosRetrieveApiArg = {
  eventId: string
  /** A unique integer value identifying this Fotka z akce. */
  id: number
}
export type FrontendEventsRecordPhotosUpdateApiResponse =
  /** status 200  */ EventPhoto
export type FrontendEventsRecordPhotosUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Fotka z akce. */
  id: number
  eventPhoto: EventPhoto
}
export type FrontendEventsRecordPhotosPartialUpdateApiResponse =
  /** status 200  */ EventPhoto
export type FrontendEventsRecordPhotosPartialUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Fotka z akce. */
  id: number
  patchedEventPhoto: PatchedEventPhoto
}
export type FrontendEventsRecordPhotosDestroyApiResponse = unknown
export type FrontendEventsRecordPhotosDestroyApiArg = {
  eventId: string
  /** A unique integer value identifying this Fotka z akce. */
  id: number
}
export type FrontendEventsRegisteredListApiResponse =
  /** status 200  */ PaginatedUserList
export type FrontendEventsRegisteredListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  _search_id?: string[]
  eventId: string
  /** Více hodnot lze oddělit čárkami. */
  id?: string[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsRegisteredRetrieveApiResponse =
  /** status 200  */ User
export type FrontendEventsRegisteredRetrieveApiArg = {
  eventId: string
  /** A UUID string identifying this Uživatel. */
  id: string
}
export type FrontendEventsRegistrationApplicationsListApiResponse =
  /** status 200  */ PaginatedEventApplicationList
export type FrontendEventsRegistrationApplicationsListApiArg = {
  eventId: string
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsRegistrationApplicationsCreateApiResponse =
  /** status 201  */ EventApplication
export type FrontendEventsRegistrationApplicationsCreateApiArg = {
  eventId: string
  eventApplication: EventApplication
}
export type FrontendEventsRegistrationApplicationsRetrieveApiResponse =
  /** status 200  */ EventApplication
export type FrontendEventsRegistrationApplicationsRetrieveApiArg = {
  eventId: string
  /** A unique integer value identifying this Přihláška na akci. */
  id: number
}
export type FrontendEventsRegistrationApplicationsUpdateApiResponse =
  /** status 200  */ EventApplication
export type FrontendEventsRegistrationApplicationsUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Přihláška na akci. */
  id: number
  eventApplication: EventApplication
}
export type FrontendEventsRegistrationApplicationsPartialUpdateApiResponse =
  /** status 200  */ EventApplication
export type FrontendEventsRegistrationApplicationsPartialUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Přihláška na akci. */
  id: number
  patchedEventApplication: PatchedEventApplication
}
export type FrontendEventsRegistrationApplicationsDestroyApiResponse = unknown
export type FrontendEventsRegistrationApplicationsDestroyApiArg = {
  eventId: string
  /** A unique integer value identifying this Přihláška na akci. */
  id: number
}
export type FrontendEventsRegistrationQuestionnaireQuestionsListApiResponse =
  /** status 200  */ PaginatedQuestionList
export type FrontendEventsRegistrationQuestionnaireQuestionsListApiArg = {
  eventId: string
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendEventsRegistrationQuestionnaireQuestionsCreateApiResponse =
  /** status 201  */ Question
export type FrontendEventsRegistrationQuestionnaireQuestionsCreateApiArg = {
  eventId: string
  question: Question
}
export type FrontendEventsRegistrationQuestionnaireQuestionsRetrieveApiResponse =
  /** status 200  */ Question
export type FrontendEventsRegistrationQuestionnaireQuestionsRetrieveApiArg = {
  eventId: string
  /** A unique integer value identifying this Otázka dotazníku. */
  id: number
}
export type FrontendEventsRegistrationQuestionnaireQuestionsUpdateApiResponse =
  /** status 200  */ Question
export type FrontendEventsRegistrationQuestionnaireQuestionsUpdateApiArg = {
  eventId: string
  /** A unique integer value identifying this Otázka dotazníku. */
  id: number
  question: Question
}
export type FrontendEventsRegistrationQuestionnaireQuestionsPartialUpdateApiResponse =
  /** status 200  */ Question
export type FrontendEventsRegistrationQuestionnaireQuestionsPartialUpdateApiArg =
  {
    eventId: string
    /** A unique integer value identifying this Otázka dotazníku. */
    id: number
    patchedQuestion: PatchedQuestion
  }
export type FrontendEventsRegistrationQuestionnaireQuestionsDestroyApiResponse =
  unknown
export type FrontendEventsRegistrationQuestionnaireQuestionsDestroyApiArg = {
  eventId: string
  /** A unique integer value identifying this Otázka dotazníku. */
  id: number
}
export type FrontendEventsRetrieveApiResponse = /** status 200  */ Event
export type FrontendEventsRetrieveApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
}
export type FrontendEventsUpdateApiResponse = /** status 200  */ Event
export type FrontendEventsUpdateApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
  event: Event
}
export type FrontendEventsPartialUpdateApiResponse = /** status 200  */ Event
export type FrontendEventsPartialUpdateApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
  patchedEvent: PatchedEvent
}
export type FrontendEventsDestroyApiResponse = unknown
export type FrontendEventsDestroyApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
}
export type FrontendGetUnknownUserRetrieveApiResponse = /** status 200  */ User
export type FrontendGetUnknownUserRetrieveApiArg = {
  birthday: string
  firstName: string
  lastName: string
}
export type FrontendLocationsListApiResponse =
  /** status 200  */ PaginatedLocationList
export type FrontendLocationsListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  id?: number[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendLocationsCreateApiResponse = /** status 201  */ Location
export type FrontendLocationsCreateApiArg = {
  location: Location
}
export type FrontendLocationsRetrieveApiResponse = /** status 200  */ Location
export type FrontendLocationsRetrieveApiArg = {
  /** A unique integer value identifying this Lokalita. */
  id: number
}
export type FrontendLocationsUpdateApiResponse = /** status 200  */ Location
export type FrontendLocationsUpdateApiArg = {
  /** A unique integer value identifying this Lokalita. */
  id: number
  location: Location
}
export type FrontendLocationsPartialUpdateApiResponse =
  /** status 200  */ Location
export type FrontendLocationsPartialUpdateApiArg = {
  /** A unique integer value identifying this Lokalita. */
  id: number
  patchedLocation: PatchedLocation
}
export type FrontendLocationsDestroyApiResponse = unknown
export type FrontendLocationsDestroyApiArg = {
  /** A unique integer value identifying this Lokalita. */
  id: number
}
export type FrontendSearchUsersListApiResponse =
  /** status 200  */ PaginatedUserSearchList
export type FrontendSearchUsersListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendUsersListApiResponse = /** status 200  */ PaginatedUserList
export type FrontendUsersListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  _search_id?: string[]
  /** Více hodnot lze oddělit čárkami. */
  id?: string[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type FrontendUsersCreateApiResponse = /** status 201  */ User
export type FrontendUsersCreateApiArg = {
  user: User
}
export type FrontendUsersRetrieveApiResponse = /** status 200  */ User
export type FrontendUsersRetrieveApiArg = {
  /** A UUID string identifying this Uživatel. */
  id: string
}
export type FrontendUsersUpdateApiResponse = /** status 200  */ User
export type FrontendUsersUpdateApiArg = {
  /** A UUID string identifying this Uživatel. */
  id: string
  user: User
}
export type FrontendUsersPartialUpdateApiResponse = /** status 200  */ User
export type FrontendUsersPartialUpdateApiArg = {
  /** A UUID string identifying this Uživatel. */
  id: string
  patchedUser: PatchedUser
}
export type FrontendUsersDestroyApiResponse = unknown
export type FrontendUsersDestroyApiArg = {
  /** A UUID string identifying this Uživatel. */
  id: string
}
export type FrontendUsersEventsWhereWasOrganizerListApiResponse =
  /** status 200  */ PaginatedEventList
export type FrontendUsersEventsWhereWasOrganizerListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  id?: number[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
  userId: string
}
export type FrontendUsersEventsWhereWasOrganizerRetrieveApiResponse =
  /** status 200  */ Event
export type FrontendUsersEventsWhereWasOrganizerRetrieveApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
  userId: string
}
export type FrontendUsersOpportunitiesListApiResponse =
  /** status 200  */ PaginatedOpportunityList
export type FrontendUsersOpportunitiesListApiArg = {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
  userId: string
}
export type FrontendUsersOpportunitiesCreateApiResponse =
  /** status 201  */ Opportunity
export type FrontendUsersOpportunitiesCreateApiArg = {
  userId: string
  opportunity: Opportunity
}
export type FrontendUsersOpportunitiesRetrieveApiResponse =
  /** status 200  */ Opportunity
export type FrontendUsersOpportunitiesRetrieveApiArg = {
  /** A unique integer value identifying this Příležitost. */
  id: number
  userId: string
}
export type FrontendUsersOpportunitiesUpdateApiResponse =
  /** status 200  */ Opportunity
export type FrontendUsersOpportunitiesUpdateApiArg = {
  /** A unique integer value identifying this Příležitost. */
  id: number
  userId: string
  opportunity: Opportunity
}
export type FrontendUsersOpportunitiesPartialUpdateApiResponse =
  /** status 200  */ Opportunity
export type FrontendUsersOpportunitiesPartialUpdateApiArg = {
  /** A unique integer value identifying this Příležitost. */
  id: number
  userId: string
  patchedOpportunity: PatchedOpportunity
}
export type FrontendUsersOpportunitiesDestroyApiResponse = unknown
export type FrontendUsersOpportunitiesDestroyApiArg = {
  /** A unique integer value identifying this Příležitost. */
  id: number
  userId: string
}
export type FrontendUsersParticipatedInEventsListApiResponse =
  /** status 200  */ PaginatedEventList
export type FrontendUsersParticipatedInEventsListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  id?: number[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
  userId: string
}
export type FrontendUsersParticipatedInEventsRetrieveApiResponse =
  /** status 200  */ Event
export type FrontendUsersParticipatedInEventsRetrieveApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
  userId: string
}
export type FrontendUsersRegisteredInEventsListApiResponse =
  /** status 200  */ PaginatedEventList
export type FrontendUsersRegisteredInEventsListApiArg = {
  /** Více hodnot lze oddělit čárkami. */
  id?: number[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
  userId: string
}
export type FrontendUsersRegisteredInEventsRetrieveApiResponse =
  /** status 200  */ Event
export type FrontendUsersRegisteredInEventsRetrieveApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
  userId: string
}
export type WebAdministrationUnitsListApiResponse =
  /** status 200  */ PaginatedAdministrationUnitList
export type WebAdministrationUnitsListApiArg = {
  /** Více hodnot lze oddělit čárkami.
    
    * `basic_section` - Základní článek
    * `headquarter` - Ústředí
    * `regional_center` - Regionální centrum
    * `club` - Klub */
  category?: ('basic_section' | 'club' | 'headquarter' | 'regional_center')[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type WebAdministrationUnitsRetrieveApiResponse =
  /** status 200  */ AdministrationUnit
export type WebAdministrationUnitsRetrieveApiArg = {
  /** A unique integer value identifying this Organizační jednotka. */
  id: number
}
export type WebEventsListApiResponse = /** status 200  */ PaginatedEventList
export type WebEventsListApiArg = {
  /** Více hodnot lze oddělit čárkami.
    
    * `1` - Brontík */
  administrationUnit?: 1[]
  /** Více hodnot lze oddělit čárkami.
    
    * `internal__general_meeting` - Interní - Valná hromada
    * `internal__volunteer_meeting` - Interní - Schůzka dobrovolníků, týmovka
    * `internal__section_meeting` - Interní - Oddílová, družinová schůzka
    * `public__volunteering` - Veřejná - Dobrovolnická
    * `public__only_experiential` - Veřejná - Čistě zážitková
    * `public__educational__lecture` - Veřejná - Vzdělávací - Přednáška
    * `public__educational__course` - Veřejná - Vzdělávací - Kurz, školení, exkurze
    * `public__educational__ohb` - Veřejná - Vzdělávací - OHB
    * `public__educational__educational` - Veřejná - Vzdělávací - Výukový program
    * `public__educational__educational_with_stay` - Veřejná - Vzdělávací - Pobytový výukový program
    * `public__club__lecture` - Veřejná - Klub - Přednáška
    * `public__club__meeting` - Veřejná - Klub - Setkání
    * `public__other__for_public` - Veřejná - Ostatní - Akce pro veřejnost
    * `public__other__exhibition` - Veřejná - Ostatní - Výstava
    * `public__other__eco_tent` - Veřejná - Ostatní - Ekostan */
  category?: (
    | 'internal__general_meeting'
    | 'internal__section_meeting'
    | 'internal__volunteer_meeting'
    | 'public__club__lecture'
    | 'public__club__meeting'
    | 'public__educational__course'
    | 'public__educational__educational'
    | 'public__educational__educational_with_stay'
    | 'public__educational__lecture'
    | 'public__educational__ohb'
    | 'public__only_experiential'
    | 'public__other__eco_tent'
    | 'public__other__exhibition'
    | 'public__other__for_public'
    | 'public__volunteering'
  )[]
  duration?: number
  durationGte?: number
  durationLte?: number
  endGte?: string
  endLte?: string
  /** Více hodnot lze oddělit čárkami.
    
    * `camp` - Tábor
    * `weekend_event` - Víkendovka
    * `other` - Ostatní */
  group?: ('camp' | 'other' | 'weekend_event')[]
  /** Více hodnot lze oddělit čárkami.
    
    * `for_all` - pro všechny
    * `for_young_and_adult` - pro mládež a dospělé
    * `for_kids` - pro děti
    * `for_parents_with_kids` - pro rodiče s dětmi
    * `for_first_time_participant` - pro prvoúčastníky */
  intendedFor?: (
    | 'for_all'
    | 'for_first_time_participant'
    | 'for_kids'
    | 'for_parents_with_kids'
    | 'for_young_and_adult'
  )[]
  /** Řazení
    
    * `start` - Start
    * `-start` - Start (sestupně)
    * `end` - End
    * `-end` - End (sestupně) */
  ordering?: ('-end' | '-start' | 'end' | 'start')[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** Více hodnot lze oddělit čárkami.
    
    * `monuments` - Akce památky
    * `nature` - Akce příroda
    * `kids` - BRĎO
    * `eco_tent` - Ekostan
    * `holidays_with_brontosaurus` - PsB (Prázdniny s Brontosaurem = vícedenní letní akce)
    * `education` - Vzdělávání
    * `international` - Mezinárodní
    * `none` - Žádný */
  program?: (
    | 'eco_tent'
    | 'education'
    | 'holidays_with_brontosaurus'
    | 'international'
    | 'kids'
    | 'monuments'
    | 'nature'
    | 'none'
  )[]
  /** A search term. */
  search?: string
  startGte?: string
  startLte?: string
}
export type WebEventsRetrieveApiResponse = /** status 200  */ Event
export type WebEventsRetrieveApiArg = {
  /** A unique integer value identifying this Akce. */
  id: number
}
export type WebOpportunitiesListApiResponse =
  /** status 200  */ PaginatedOpportunityList
export type WebOpportunitiesListApiArg = {
  /** Více hodnot lze oddělit čárkami.
    
    * `organizing` - Organizování akcí
    * `collaboration` - Spolupráce
    * `location_help` - Pomoc lokalitě */
  category?: ('collaboration' | 'location_help' | 'organizing')[]
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}
export type WebOpportunitiesRetrieveApiResponse = /** status 200  */ Opportunity
export type WebOpportunitiesRetrieveApiArg = {
  /** A unique integer value identifying this Příležitost. */
  id: number
}
export type TokenResponse = {
  token: string
}
export type LoginRequest = {
  email: string
  password: string
}
export type ResetPasswordRequest = {
  email: string
  code: string
  password: string
}
export type SendVerificationLinkRequest = {
  email: string
}
export type UserIdResponse = {
  id: number
}
export type AdministrationUnitCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedAdministrationUnitCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: AdministrationUnitCategory[]
}
export type DietCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedDietCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: DietCategory[]
}
export type DonationSourceCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedDonationSourceCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: DonationSourceCategory[]
}
export type EventCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedEventCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventCategory[]
}
export type EventGroupCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedEventGroupCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventGroupCategory[]
}
export type EventIntendedForCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedEventIntendedForCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventIntendedForCategory[]
}
export type EventProgramCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedEventProgramCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventProgramCategory[]
}
export type GrantCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedGrantCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: GrantCategory[]
}
export type HealthInsuranceCompany = {
  id: number
  name: string
  slug: string
}
export type PaginatedHealthInsuranceCompanyList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: HealthInsuranceCompany[]
}
export type LocationAccessibilityCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedLocationAccessibilityCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: LocationAccessibilityCategory[]
}
export type LocationProgramCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedLocationProgramCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: LocationProgramCategory[]
}
export type MembershipCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedMembershipCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: MembershipCategory[]
}
export type OpportunityCategory = {
  id: number
  name: string
  description: string
  slug: string
}
export type PaginatedOpportunityCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: OpportunityCategory[]
}
export type OrganizerRoleCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedOrganizerRoleCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: OrganizerRoleCategory[]
}
export type PronounCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedPronounCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: PronounCategory[]
}
export type QualificationCategory = {
  id: number
  name: string
  slug: string
  parents: number[]
  can_approve: number[]
}
export type PaginatedQualificationCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: QualificationCategory[]
}
export type Region = {
  id: number
  name: string
}
export type PaginatedRegionList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: Region[]
}
export type RoleCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedRoleCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: RoleCategory[]
}
export type TeamRoleCategory = {
  id: number
  name: string
  slug: string
}
export type PaginatedTeamRoleCategoryList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: TeamRoleCategory[]
}
export type DashboardItem = {
  date: string
  name: string
  description?: string
}
export type PaginatedDashboardItemList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: DashboardItem[]
}
export type EventDraft = {
  id: number
  data: {
    [key: string]: any
  }
}
export type PaginatedEventDraftList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventDraft[]
}
export type PatchedEventDraft = {
  id?: number
  data?: {
    [key: string]: any
  }
}
export type Finance = {
  bank_account_number?: string
  grant_category: GrantCategory
  grant_amount?: number | null
  total_event_cost?: number | null
  budget?: string
}
export type Propagation = {
  is_shown_on_web: boolean
  minimum_age?: number | null
  maximum_age?: number | null
  cost: string
  accommodation?: string
  working_hours?: number | null
  working_days?: number | null
  diets: DietCategory[]
  organizers: string
  web_url?: string
  _contact_url?: string
  invitation_text_introduction: string
  invitation_text_practical_information: string
  invitation_text_work_description?: string
  invitation_text_about_us?: string
  contact_name: string
  contact_phone?: string
  contact_email?: string
}
export type VipPropagation = {
  goals_of_event: string
  program: string
  short_invitation_text: string
  rover_propagation?: boolean
}
export type Questionnaire = {
  introduction?: string
  after_submit_text?: string
}
export type Registration = {
  is_registration_required?: boolean
  alternative_registration_link?: string
  is_event_full?: boolean
  questionnaire: Questionnaire | null
}
export type EventContact = {
  first_name: string
  last_name: string
  email?: string
  phone?: string
}
export type Record = {
  total_hours_worked?: number | null
  comment_on_work_done?: string
  participants?: string[]
  number_of_participants?: number | null
  number_of_participants_under_26?: number | null
  note?: string
  contacts?: EventContact[]
}
export type Event = {
  id: number
  name: string
  is_canceled?: boolean
  is_complete?: boolean
  is_closed?: boolean
  start: string
  start_time?: string | null
  end: string
  number_of_sub_events?: number
  location: number
  online_link?: string
  group: EventGroupCategory
  category: EventCategory
  program: EventProgramCategory
  intended_for: EventIntendedForCategory
  administration_units: number[]
  main_organizer: string
  other_organizers?: string[]
  is_attendance_list_required?: boolean
  internal_note?: string
  duration: number
  finance: Finance | null
  propagation: Propagation | null
  vip_propagation: VipPropagation | null
  registration: Registration | null
  record: Record | null
}
export type PaginatedEventList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: Event[]
}
export type FinanceReceipt = {
  id: number
  receipt: string
}
export type PaginatedFinanceReceiptList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: FinanceReceipt[]
}
export type PatchedFinanceReceipt = {
  id?: number
  receipt?: string
}
export type ClosePerson = {
  first_name: string
  last_name: string
  email?: string
  phone?: string
}
export type Donation = {
  donated_at: string
  amount: number
  donation_source: DonationSourceCategory
}
export type Donor = {
  subscribed_to_newsletter?: boolean
  is_public?: boolean
  date_joined: string
  regional_center_support?: number | null
  basic_section_support?: number | null
  variable_symbols: number[]
  donations: Donation[]
}
export type OfferedHelp = {
  programs: EventProgramCategory[]
  organizer_roles: OrganizerRoleCategory[]
  additional_organizer_role?: string
  team_roles: TeamRoleCategory[]
  additional_team_role?: string
  info?: string
}
export type UserAddress = {
  street: string
  city: string
  zip_code: string
  region: Region
}
export type UserContactAddress = {
  street: string
  city: string
  zip_code: string
  region: Region
}
export type EycaCard = {
  photo: string
  number: string
  submitted_for_creation: boolean
  sent_to_user: boolean
  valid_till: string
}
export type Membership = {
  category: MembershipCategory
  administration_unit: number
  year: number
}
export type QualificationApprovedBy = {
  first_name: string
  last_name: string
  email?: string | null
  phone?: string
}
export type Qualification = {
  category: QualificationCategory
  valid_since: string
  valid_till: string
  approved_by: QualificationApprovedBy
}
export type User = {
  id: string
  _search_id: string
  first_name: string
  last_name: string
  nickname?: string
  birth_name?: string
  display_name: string
  phone?: string
  email?: string | null
  all_emails: string[]
  birthday: string
  close_person: ClosePerson | null
  subscribed_to_newsletter?: boolean
  health_insurance_company: HealthInsuranceCompany
  health_issues?: string
  pronoun: PronounCategory
  is_active: boolean
  date_joined: string
  roles: RoleCategory[]
  donor: Donor | null
  offers: OfferedHelp | null
  address: UserAddress
  contact_address: UserContactAddress | null
  eyca_card: EycaCard | null
  memberships: Membership[]
  qualifications: Qualification[]
}
export type PaginatedUserList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: User[]
}
export type EventPropagationImage = {
  id: number
  order: number
  image: string
}
export type PaginatedEventPropagationImageList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventPropagationImage[]
}
export type PatchedEventPropagationImage = {
  id?: number
  order?: number
  image?: string
}
export type AttendanceListPage = {
  id: number
  page?: string | null
}
export type PaginatedAttendanceListPageList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: AttendanceListPage[]
}
export type PatchedAttendanceListPage = {
  id?: number
  page?: string | null
}
export type EventPhoto = {
  id: number
  photo: string
}
export type PaginatedEventPhotoList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventPhoto[]
}
export type PatchedEventPhoto = {
  id?: number
  photo?: string
}
export type StateEnum = 'pending' | 'cancelled' | 'rejected' | 'approved'
export type EventApplicationClosePerson = {
  first_name: string
  last_name: string
  email?: string
  phone?: string
}
export type EventApplicationAddress = {
  street: string
  city: string
  zip_code: string
  region: Region
}
export type Question = {
  id: number
  question: string
  data?: {
    [key: string]: any
  }
  is_required?: boolean
  order?: number
}
export type Answer = {
  question: Question
  answer: string
  data?: {
    [key: string]: any
  }
}
export type EventApplication = {
  id: number
  user?: string | null
  state: StateEnum
  first_name: string
  last_name: string
  nickname?: string
  phone?: string
  email?: string | null
  birthday?: string | null
  health_issues?: string
  pronoun: PronounCategory
  created_at: string
  close_person: EventApplicationClosePerson | null
  address: EventApplicationAddress | null
  answers: Answer[]
  note?: string
  is_child_application?: boolean
}
export type PaginatedEventApplicationList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: EventApplication[]
}
export type PatchedEventApplication = {
  id?: number
  user?: string | null
  state?: StateEnum
  first_name?: string
  last_name?: string
  nickname?: string
  phone?: string
  email?: string | null
  birthday?: string | null
  health_issues?: string
  pronoun?: number | null
  created_at?: string
  close_person?: EventApplicationClosePerson | null
  address?: EventApplicationAddress | null
  answers?: Answer[]
  note?: string
  is_child_application?: boolean
}
export type PaginatedQuestionList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: Question[]
}
export type PatchedQuestion = {
  id?: number
  question?: string
  data?: {
    [key: string]: any
  }
  is_required?: boolean
  order?: number
}
export type PatchedEvent = {
  id?: number
  name?: string
  is_canceled?: boolean
  is_complete?: boolean
  is_closed?: boolean
  start?: string
  start_time?: string | null
  end?: string
  number_of_sub_events?: number
  location?: number
  online_link?: string
  group?: number
  category?: number
  program?: number
  intended_for?: number
  administration_units?: number[]
  main_organizer?: string
  other_organizers?: string[]
  is_attendance_list_required?: boolean
  internal_note?: string
  duration?: number
  finance?: Finance | null
  propagation?: Propagation | null
  vip_propagation?: VipPropagation | null
  registration?: Registration | null
  record?: Record | null
}
export type LocationPatron = {
  first_name: string
  last_name: string
  email?: string
  phone?: string
}
export type LocationContactPerson = {
  first_name: string
  last_name: string
  email?: string
  phone?: string
}
export type Location = {
  id: number
  name: string
  description?: string
  patron: LocationPatron | null
  contact_person: LocationContactPerson | null
  is_fully_specified?: boolean
  for_beginners?: boolean
  is_full?: boolean
  is_unexplored?: boolean
  program: LocationProgramCategory
  accessibility_from_prague: LocationAccessibilityCategory
  accessibility_from_brno: LocationAccessibilityCategory
  volunteering_work?: string
  volunteering_work_done?: string
  volunteering_work_goals?: string
  options_around?: string
  facilities?: string
  web?: string
  address?: string
  gps_location: {
    type?: 'Point'
    coordinates?: number[]
  }
  region: Region
}
export type PaginatedLocationList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: Location[]
}
export type PatchedLocation = {
  id?: number
  name?: string
  description?: string
  patron?: LocationPatron | null
  contact_person?: LocationContactPerson | null
  is_fully_specified?: boolean
  for_beginners?: boolean
  is_full?: boolean
  is_unexplored?: boolean
  program?: number | null
  accessibility_from_prague?: number | null
  accessibility_from_brno?: number | null
  volunteering_work?: string
  volunteering_work_done?: string
  volunteering_work_goals?: string
  options_around?: string
  facilities?: string
  web?: string
  address?: string
  gps_location?: {
    type?: 'Point'
    coordinates?: number[]
  }
  region?: number
}
export type UserSearch = {
  _search_id: string
  display_name: string
  first_name: string
  last_name: string
}
export type PaginatedUserSearchList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: UserSearch[]
}
export type PatchedUser = {
  id?: string
  _search_id?: string
  first_name?: string
  last_name?: string
  nickname?: string
  birth_name?: string
  display_name?: string
  phone?: string
  email?: string | null
  all_emails?: string[]
  birthday?: string
  close_person?: ClosePerson | null
  subscribed_to_newsletter?: boolean
  health_insurance_company?: number | null
  health_issues?: string
  pronoun?: number | null
  is_active?: boolean
  date_joined?: string
  roles?: number[]
  donor?: Donor | null
  offers?: OfferedHelp | null
  address?: UserAddress
  contact_address?: UserContactAddress | null
  eyca_card?: EycaCard | null
  memberships?: Membership[]
  qualifications?: Qualification[]
}
export type Opportunity = {
  id: number
  category: OpportunityCategory
  name: string
  start: string
  end: string
  on_web_start: string
  on_web_end: string
  location: number
  introduction: string
  description: string
  location_benefits?: string
  personal_benefits: string
  requirements?: string
  contact_name?: string
  contact_phone?: string
  contact_email?: string
  image: string
}
export type PaginatedOpportunityList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: Opportunity[]
}
export type PatchedOpportunity = {
  id?: number
  category?: number
  name?: string
  start?: string
  end?: string
  on_web_start?: string
  on_web_end?: string
  location?: number
  introduction?: string
  description?: string
  location_benefits?: string
  personal_benefits?: string
  requirements?: string
  contact_name?: string
  contact_phone?: string
  contact_email?: string
  image?: string
}
export type AdministrationUnit = {
  id: number
  name: string
  abbreviation: string
  is_for_kids: boolean
  phone: string
  email: string
  www?: string
  ic?: string
  address: string
  contact_address: string
  bank_account_number?: string
  existed_since?: string | null
  existed_till?: string | null
  gps_location?: {
    type?: 'Point'
    coordinates?: number[]
  } | null
  category: AdministrationUnitCategory
  chairman: User
  vice_chairman: User
  manager: User
  board_members: User[]
}
export type PaginatedAdministrationUnitList = {
  count?: number
  next?: string | null
  previous?: string | null
  results?: AdministrationUnit[]
}
export const {
  useAuthLoginCreateMutation,
  useAuthLogoutCreateMutation,
  useAuthResetPasswordCreateMutation,
  useAuthSendVerificationLinkCreateMutation,
  useAuthWhoamiRetrieveQuery,
  useCategoriesAdministrationUnitCategoriesListQuery,
  useCategoriesAdministrationUnitCategoriesRetrieveQuery,
  useCategoriesDietCategoriesListQuery,
  useCategoriesDietCategoriesRetrieveQuery,
  useCategoriesDonationSourceCategoriesListQuery,
  useCategoriesDonationSourceCategoriesRetrieveQuery,
  useCategoriesEventCategoriesListQuery,
  useCategoriesEventCategoriesRetrieveQuery,
  useCategoriesEventGroupCategoriesListQuery,
  useCategoriesEventGroupCategoriesRetrieveQuery,
  useCategoriesEventIntendedForCategoriesListQuery,
  useCategoriesEventIntendedForCategoriesRetrieveQuery,
  useCategoriesEventProgramCategoriesListQuery,
  useCategoriesEventProgramCategoriesRetrieveQuery,
  useCategoriesGrantCategoriesListQuery,
  useCategoriesGrantCategoriesRetrieveQuery,
  useCategoriesHealthInsuranceCompaniesListQuery,
  useCategoriesHealthInsuranceCompaniesRetrieveQuery,
  useCategoriesLocationAccessibilityCategoriesListQuery,
  useCategoriesLocationAccessibilityCategoriesRetrieveQuery,
  useCategoriesLocationProgramCategoriesListQuery,
  useCategoriesLocationProgramCategoriesRetrieveQuery,
  useCategoriesMembershipCategoriesListQuery,
  useCategoriesMembershipCategoriesRetrieveQuery,
  useCategoriesOpportunityCategoriesListQuery,
  useCategoriesOpportunityCategoriesRetrieveQuery,
  useCategoriesOrganizerRoleCategoriesListQuery,
  useCategoriesOrganizerRoleCategoriesRetrieveQuery,
  useCategoriesPronounCategoriesListQuery,
  useCategoriesPronounCategoriesRetrieveQuery,
  useCategoriesQualificationCategoriesListQuery,
  useCategoriesQualificationCategoriesRetrieveQuery,
  useCategoriesRegionsListQuery,
  useCategoriesRegionsRetrieveQuery,
  useCategoriesRoleCategoriesListQuery,
  useCategoriesRoleCategoriesRetrieveQuery,
  useCategoriesTeamRoleCategoriesListQuery,
  useCategoriesTeamRoleCategoriesRetrieveQuery,
  useFrontendDashboardItemsListQuery,
  useFrontendDashboardItemsRetrieveQuery,
  useFrontendEventDraftsListQuery,
  useFrontendEventDraftsCreateMutation,
  useFrontendEventDraftsRetrieveQuery,
  useFrontendEventDraftsUpdateMutation,
  useFrontendEventDraftsPartialUpdateMutation,
  useFrontendEventDraftsDestroyMutation,
  useFrontendEventsListQuery,
  useFrontendEventsCreateMutation,
  useFrontendEventsFinanceReceiptsListQuery,
  useFrontendEventsFinanceReceiptsCreateMutation,
  useFrontendEventsFinanceReceiptsRetrieveQuery,
  useFrontendEventsFinanceReceiptsUpdateMutation,
  useFrontendEventsFinanceReceiptsPartialUpdateMutation,
  useFrontendEventsFinanceReceiptsDestroyMutation,
  useFrontendEventsGetAttendanceListRetrieveQuery,
  useFrontendEventsGetParticipantsListRetrieveQuery,
  useFrontendEventsOrganizersListQuery,
  useFrontendEventsOrganizersRetrieveQuery,
  useFrontendEventsPropagationImagesListQuery,
  useFrontendEventsPropagationImagesCreateMutation,
  useFrontendEventsPropagationImagesRetrieveQuery,
  useFrontendEventsPropagationImagesUpdateMutation,
  useFrontendEventsPropagationImagesPartialUpdateMutation,
  useFrontendEventsPropagationImagesDestroyMutation,
  useFrontendEventsRecordAttendanceListPagesListQuery,
  useFrontendEventsRecordAttendanceListPagesCreateMutation,
  useFrontendEventsRecordAttendanceListPagesRetrieveQuery,
  useFrontendEventsRecordAttendanceListPagesUpdateMutation,
  useFrontendEventsRecordAttendanceListPagesPartialUpdateMutation,
  useFrontendEventsRecordAttendanceListPagesDestroyMutation,
  useFrontendEventsRecordParticipantsListQuery,
  useFrontendEventsRecordParticipantsRetrieveQuery,
  useFrontendEventsRecordPhotosListQuery,
  useFrontendEventsRecordPhotosCreateMutation,
  useFrontendEventsRecordPhotosRetrieveQuery,
  useFrontendEventsRecordPhotosUpdateMutation,
  useFrontendEventsRecordPhotosPartialUpdateMutation,
  useFrontendEventsRecordPhotosDestroyMutation,
  useFrontendEventsRegisteredListQuery,
  useFrontendEventsRegisteredRetrieveQuery,
  useFrontendEventsRegistrationApplicationsListQuery,
  useFrontendEventsRegistrationApplicationsCreateMutation,
  useFrontendEventsRegistrationApplicationsRetrieveQuery,
  useFrontendEventsRegistrationApplicationsUpdateMutation,
  useFrontendEventsRegistrationApplicationsPartialUpdateMutation,
  useFrontendEventsRegistrationApplicationsDestroyMutation,
  useFrontendEventsRegistrationQuestionnaireQuestionsListQuery,
  useFrontendEventsRegistrationQuestionnaireQuestionsCreateMutation,
  useFrontendEventsRegistrationQuestionnaireQuestionsRetrieveQuery,
  useFrontendEventsRegistrationQuestionnaireQuestionsUpdateMutation,
  useFrontendEventsRegistrationQuestionnaireQuestionsPartialUpdateMutation,
  useFrontendEventsRegistrationQuestionnaireQuestionsDestroyMutation,
  useFrontendEventsRetrieveQuery,
  useFrontendEventsUpdateMutation,
  useFrontendEventsPartialUpdateMutation,
  useFrontendEventsDestroyMutation,
  useFrontendGetUnknownUserRetrieveQuery,
  useFrontendLocationsListQuery,
  useFrontendLocationsCreateMutation,
  useFrontendLocationsRetrieveQuery,
  useFrontendLocationsUpdateMutation,
  useFrontendLocationsPartialUpdateMutation,
  useFrontendLocationsDestroyMutation,
  useFrontendSearchUsersListQuery,
  useFrontendUsersListQuery,
  useFrontendUsersCreateMutation,
  useFrontendUsersRetrieveQuery,
  useFrontendUsersUpdateMutation,
  useFrontendUsersPartialUpdateMutation,
  useFrontendUsersDestroyMutation,
  useFrontendUsersEventsWhereWasOrganizerListQuery,
  useFrontendUsersEventsWhereWasOrganizerRetrieveQuery,
  useFrontendUsersOpportunitiesListQuery,
  useFrontendUsersOpportunitiesCreateMutation,
  useFrontendUsersOpportunitiesRetrieveQuery,
  useFrontendUsersOpportunitiesUpdateMutation,
  useFrontendUsersOpportunitiesPartialUpdateMutation,
  useFrontendUsersOpportunitiesDestroyMutation,
  useFrontendUsersParticipatedInEventsListQuery,
  useFrontendUsersParticipatedInEventsRetrieveQuery,
  useFrontendUsersRegisteredInEventsListQuery,
  useFrontendUsersRegisteredInEventsRetrieveQuery,
  useWebAdministrationUnitsListQuery,
  useWebAdministrationUnitsRetrieveQuery,
  useWebEventsListQuery,
  useWebEventsRetrieveQuery,
  useWebOpportunitiesListQuery,
  useWebOpportunitiesRetrieveQuery,
} = injectedRtkApi
