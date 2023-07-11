import { Routes } from 'config/sentry'
import { AdminOutlet } from 'layout/AdminOutlet'
import { AuthenticatedOutlet } from 'layout/AuthenticatedOutlet'
import { EventOrganizerOutlet } from 'layout/EventOrganizerOutlet'
import { MixedOutlet } from 'layout/MixedOutlet'
import { OrganizerOutlet } from 'layout/OrganizerOutlet'
import { UnauthenticatedOutlet } from 'layout/UnauthenticatedOutlet'
import { EventOutlet } from 'org/EventOutlet'
import { OpportunityOutlet } from 'org/OpportunityOutlet'
import { CloseEvent } from 'org/pages/CloseEvent'
import { CreateEvent } from 'org/pages/CreateEvent'
import { CreateOpportunity } from 'org/pages/CreateOpportunity'
import { EventApplications } from 'org/pages/EventApplications'
import {
  ActiveEvents,
  AllEvents,
  EventsLayout,
  UnfinishedEvents,
} from 'org/pages/EventList'
import { Home as OrgHome } from 'org/pages/Home'
import { OpportunityList } from 'org/pages/OpportunityList'
import { UpdateEvent } from 'org/pages/UpdateEvent'
import { UpdateOpportunity } from 'org/pages/UpdateOpportunity'
import { ViewEvent } from 'org/pages/ViewEvent'
import { ViewOpportunity } from 'org/pages/ViewOpportunity'
import { AdminRedirect } from 'pages/AdminRedirect'
import { EventRegistration } from 'pages/EventRegistration/EventRegistration'
import { Home } from 'pages/Home'
import { Login } from 'pages/Login'
import { Logout } from 'pages/Logout'
import { NotFound } from 'pages/NotFound'
import { ResetPassword } from 'pages/ResetPassword'
import { SendResetPasswordLink } from 'pages/SendResetPasswordLink'
import { Navigate, Route } from 'react-router-dom'
import { EditProfile } from 'user/pages/EditProfile'
import { Home as UserHome } from 'user/pages/Home'
import { UserParticipatedEvents } from 'user/pages/UserParticipatedEvents'
import { UserRegisteredEvents } from 'user/pages/UserRegisteredEvents'
import { ViewMyProfile } from 'user/pages/ViewMyProfile'
import { ViewProfile } from 'user/pages/ViewProfile'
import { ProfileOutlet } from 'user/ProfileOutlet'
import { UserEventsLayout } from 'user/UserEventsLayout'

export const App = () => {
  return (
    <Routes>
      {/* Routes for both authenticated and unauthenticated users (e.g. registration for events) */}
      <Route element={<MixedOutlet />}>
        <Route
          path="/akce/:eventId/prihlasit"
          element={<EventRegistration />}
        />
      </Route>
      <Route path="/logout" element={<Logout />} />
      {/* Routes for unauthenticated users */}
      <Route element={<UnauthenticatedOutlet />}>
        <Route path="/login" element={<Login />} />
        <Route
          path="/send-reset-password-link"
          element={<SendResetPasswordLink />}
        />
        <Route path="/reset_password" element={<ResetPassword />} />
      </Route>
      {/* Routes for authenticated users */}
      <Route path="/" element={<AuthenticatedOutlet />}>
        <Route index element={<Home />} />
        {/* for now we still keep profile outside of user route
        because we use it in both user and organizer context */}
        <Route path="profil">
          <Route index element={<ViewMyProfile />} />
          <Route path=":userId" element={<ProfileOutlet />}>
            <Route index element={<ViewProfile />} />
            <Route path="upravit" element={<EditProfile />} />
          </Route>
        </Route>
        <Route path="user">
          <Route index element={<UserHome />} />
          <Route path="akce" element={<UserEventsLayout />}>
            <Route index element={<Navigate to="zucastnene" replace />} />
            <Route path="zucastnene" element={<UserParticipatedEvents />} />
            <Route path="prihlasene" element={<UserRegisteredEvents />} />
          </Route>
          <Route path="akce/:eventId" element={<EventOutlet />}>
            <Route index element={<ViewEvent readonly />} />
          </Route>
        </Route>
        <Route path="admin" element={<AdminOutlet />}>
          <Route index element={<AdminRedirect />} />
          <Route path="/admin/*" element={<AdminRedirect />} />
        </Route>
        {/* Routes for organizers */}
        <Route path="org" element={<OrganizerOutlet />}>
          <Route index element={<OrgHome />} />
          <Route path="akce/vytvorit" element={<EventOrganizerOutlet />}>
            <Route index element={<CreateEvent />} />
          </Route>
          <Route path="akce/:eventId" element={<EventOutlet />}>
            <Route index element={<ViewEvent />} />
            <Route path="prihlasky" element={<EventApplications />} />
            <Route path="upravit" element={<UpdateEvent />} />
            <Route path="uzavrit" element={<CloseEvent />} />
          </Route>
          <Route path="akce" element={<EventsLayout />}>
            <Route index element={<Navigate to="vsechny" replace />} />
            <Route path="aktualni" element={<ActiveEvents />} />
            <Route path="vsechny" element={<AllEvents />} />
            <Route path="nevyplnene" element={<UnfinishedEvents />} />
          </Route>
          <Route path="prilezitosti/vytvorit" element={<CreateOpportunity />} />
          <Route
            path="prilezitosti/:opportunityId"
            element={<OpportunityOutlet />}
          >
            <Route index element={<ViewOpportunity />} />
            <Route path="upravit" element={<UpdateOpportunity />} />
          </Route>
          <Route path="prilezitosti" element={<OpportunityList />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
