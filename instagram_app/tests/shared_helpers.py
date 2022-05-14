from django.contrib.auth import get_user_model 
import uuid 
def create_test_user(): 
    user =  get_user_model()(
        username=str(uuid.uuid4())
    )
    user.set_password(str(uuid.uuid4()))
    user.save()
    return user
def create_test_profile(): 
    return create_test_user().profile
def get_fixtures_path(): 
    return "./instagram_app/tests/fixtures/"