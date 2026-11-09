
# SafeSpace Backend - Frontend Contract

## 1. Authentication

from backend.services.auth_service import register_user, login_user

register_user(username, email, password)
login_user(email, password)

## 2. User

from backend.services.user_service import get_user_by_id, update_username

get_user_by_id(user_id)
update_username(user_id, new_username)

## 3. Community

from backend.services.community_service import (
    list_communities,
    create_community,
    join_community,
    get_user_communities
)

list_communities()
create_community(name, description)
join_community(user_id, community_id)
get_user_communities(user_id)

## 4. Post

from backend.services.post_service import (
    create_post,
    get_feed,
    get_post
)

create_post(user_id, community_id, title, content)
get_feed(community_id=None, limit=30)
get_post(post_id)

## 5. Comment

from backend.services.comment_service import add_comment, get_comments

add_comment(user_id, post_id, content, parent_comment_id=None)
get_comments(post_id)

## 6. Report

from backend.services.report_service import create_report, get_reports

create_report(reporter_id, content_type, content_id, reason)
get_reports()

## 7. Appeal

from backend.services.appeal_service import create_appeal, review_appeal

create_appeal(user_id, content_type, content_id, reason)
review_appeal(appeal_id, moderator_id, decision)

## 8. Moderation

from backend.services.moderation_service import (
    review_content,
    get_pending_content
)

review_content(moderator_id, content_type, content_id, new_status, notes)
get_pending_content()

## 9. Admin

from backend.services.admin_service import (
    get_dashboard_statistics,
    update_user_role
)

get_dashboard_statistics()
update_user_role(user_id, new_role)

## 10. History

from backend.services.history_service import get_moderation_history

get_moderation_history(content_type, content_id)
