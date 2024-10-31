from resources.auth import RegisterComplainer, LoginComplainer, Password
from resources.complaint import ComplaintListCreate, ComplaintApprove, ComplaintReject
from resources.user import User

routes = (
    (RegisterComplainer, "/register"),
    (LoginComplainer, "/login"),
    (ComplaintListCreate, "/complainers/complaints"),
    (ComplaintApprove, "/complaints/<int:complaint_id>/approve"),
    (ComplaintReject, "/complaints/<int:complaint_id>/reject"),
    (User, "/admin/users"),
    (Password, "/users/change-password"),
)
