

def send_post(user, post_index):
    user.send_post_to_users(post_index)

def enter_post_index(user):
    user.send_message("SELECT_INDEX")
    user.change_user_state ("INPUT_INDEX")


