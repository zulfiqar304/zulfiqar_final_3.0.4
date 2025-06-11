
from main import app, db, CoinConfiguration

def add_api_configs():
    """Add API configuration options to the system"""
    with app.app_context():
        try:
            # Check if API URL config already exists
            existing_url = CoinConfiguration.query.filter_by(config_name='jap_api_url').first()
            if not existing_url:
                url_config = CoinConfiguration(
                    config_name='jap_api_url',
                    coin_value=0,  # Not used for text configs
                    description='https://justanotherpanel.com/api/v2',
                    is_active=True
                )
                db.session.add(url_config)
                print("✅ JAP API URL configuration added successfully!")
            else:
                print("✅ JAP API URL configuration already exists!")

            # Check if API Key config already exists
            existing_key = CoinConfiguration.query.filter_by(config_name='jap_api_key').first()
            if not existing_key:
                key_config = CoinConfiguration(
                    config_name='jap_api_key',
                    coin_value=0,  # Not used for text configs
                    description='c88871268f8d5276927ff8c09fceb422',
                    is_active=True
                )
                db.session.add(key_config)
                print("✅ JAP API Key configuration added successfully!")
            else:
                print("✅ JAP API Key configuration already exists!")
                
            # Check if Registration Bonus config already exists
            existing_reg_bonus = CoinConfiguration.query.filter_by(config_name='registration_bonus').first()
            if not existing_reg_bonus:
                reg_bonus_config = CoinConfiguration(
                    config_name='registration_bonus',
                    coin_value=5,
                    description='Welcome bonus for new user registration',
                    is_active=True
                )
                db.session.add(reg_bonus_config)
                print("✅ Registration bonus configuration added successfully!")
            else:
                print("✅ Registration bonus configuration already exists!")
                
            # Check if Ad Watch Reward config already exists
            existing_ad_reward = CoinConfiguration.query.filter_by(config_name='ad_watch_reward').first()
            if not existing_ad_reward:
                ad_reward_config = CoinConfiguration(
                    config_name='ad_watch_reward',
                    coin_value=1,  # This will be overridden to 0.5 in the code
                    description='Reward for watching 40-second ads',
                    is_active=True
                )
                db.session.add(ad_reward_config)
                print("✅ Ad watch reward configuration added successfully!")
            else:
                print("✅ Ad watch reward configuration already exists!")

            # Check if Login Bonus Activity Requirement config already exists
            existing_activity_req = CoinConfiguration.query.filter_by(config_name='login_bonus_activity_days').first()
            if not existing_activity_req:
                activity_req_config = CoinConfiguration(
                    config_name='login_bonus_activity_days',
                    coin_value=3,
                    description='Number of days to check for ad watching activity before giving login bonus',
                    is_active=True
                )
                db.session.add(activity_req_config)
                print("✅ Login bonus activity requirement configuration added successfully!")
            else:
                print("✅ Login bonus activity requirement configuration already exists!")

            # Check if Minimum Ad Activity config already exists
            existing_min_activity = CoinConfiguration.query.filter_by(config_name='min_ads_for_login_bonus').first()
            if not existing_min_activity:
                min_activity_config = CoinConfiguration(
                    config_name='min_ads_for_login_bonus',
                    coin_value=1,
                    description='Minimum ads watched to qualify for daily login bonus',
                    is_active=True
                )
                db.session.add(min_activity_config)
                print("✅ Minimum ad activity configuration added successfully!")
            else:
                print("✅ Minimum ad activity configuration already exists!")
                
            db.session.commit()
                
        except Exception as e:
            print(f"❌ Error adding API configurations: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_api_configs()
