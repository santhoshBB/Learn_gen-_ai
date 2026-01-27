from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# State definitions
# ADD THESE 3 FUNCTIONS AT TOP OF FILE

_authenticated_sessions = set()

def is_user_authenticated(session_id: str) -> bool:
    """Check if user is authenticated"""
    return session_id in _authenticated_sessions

def set_user_authenticated(session_id: str, authenticated: bool = True):
    """Mark user as authenticated"""
    if authenticated:
        _authenticated_sessions.add(session_id)
    else:
        _authenticated_sessions.discard(session_id)


class LoginState(TypedDict):
    user_id: str
    is_authenticated: bool
    error: str | None

class FormState(TypedDict):
    user_id: str
    form_type: str  # "mobile" or "email"
    new_value: str
    confirmed: bool
    is_authenticated: bool

# ===== LOGIN FLOW =====
def check_auth(state: LoginState) -> LoginState:
    """Check if user is already authenticated"""
    # TODO: Implement actual auth check
    state["is_authenticated"] = False  # Placeholder
    return state

def collect_credentials(state: LoginState) -> LoginState:
    """Collect username/password"""
    # TODO: Implement credential collection
    return state

def authenticate(state: LoginState) -> LoginState:
    """Verify credentials"""
    state["is_authenticated"] = True
    set_user_authenticated(state["user_id"], True)  # ← ADD THIS LINE
    return state

def login_router(state: LoginState) -> Literal["collect", "success"]:
    return "success" if state["is_authenticated"] else "collect"

# Build login graph
login_graph = StateGraph(LoginState)
login_graph.add_node("check_auth", check_auth)
login_graph.add_node("collect", collect_credentials)
login_graph.add_node("authenticate", authenticate)

login_graph.set_entry_point("check_auth")
login_graph.add_conditional_edges("check_auth", login_router, {
    "collect": "collect",
    "success": END
})
login_graph.add_edge("collect", "authenticate")
login_graph.add_edge("authenticate", END)

login_workflow = login_graph.compile()


# ===== FORM CHANGE FLOW =====
def verify_login(state: FormState) -> FormState:
    """Check if user is logged in"""
    # TODO: Implement login verification
    state["is_authenticated"] = True  # Placeholder
    return state

def collect_new_value(state: FormState) -> FormState:
    """Collect new mobile/email"""
    # TODO: Implement value collection
    return state

def confirm_change(state: FormState) -> FormState:
    """Ask for confirmation"""
    # TODO: Implement confirmation
    state["confirmed"] = True
    return state

def update_database(state: FormState) -> FormState:
    """Update the value in DB"""
    # TODO: Implement DB update
    return state

def form_router(state: FormState) -> Literal["login", "collect"]:
    return "collect" if state["is_authenticated"] else "login"

def confirm_router(state: FormState) -> Literal["update", "collect"]:
    return "update" if state["confirmed"] else "collect"

# Build form graph
form_graph = StateGraph(FormState)
form_graph.add_node("verify_login", verify_login)
form_graph.add_node("collect", collect_new_value)
form_graph.add_node("confirm", confirm_change)
form_graph.add_node("update", update_database)

form_graph.set_entry_point("verify_login")
form_graph.add_conditional_edges("verify_login", form_router, {
    "login": END,  # Redirect to login
    "collect": "collect"
})
form_graph.add_edge("collect", "confirm")
form_graph.add_conditional_edges("confirm", confirm_router, {
    "update": "update",
    "collect": "collect"
})
form_graph.add_edge("update", END)

form_workflow = form_graph.compile()


# ===== WORKFLOW RUNNERS =====
def run_login_flow(session_id: str) -> dict:
    """Execute login workflow"""
    initial_state = LoginState(
        user_id=session_id,
        is_authenticated=False,
        error=None
    )
    result = login_workflow.invoke(initial_state)
    return result

def run_form_flow(session_id: str, form_type: str) -> dict:
    """Execute form change workflow"""
    initial_state = FormState(
        user_id=session_id,
        form_type=form_type,
        new_value="",
        confirmed=False,
        is_authenticated=False
    )
    result = form_workflow.invoke(initial_state)
    return result