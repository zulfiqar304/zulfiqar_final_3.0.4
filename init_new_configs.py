
from main import app, db, CoinConfiguration, AdNetwork

def init_new_configs():
    """Initialize new configurations for the updated system"""
    with app.app_context():
        try:
            # Browser login bonus
            browser_login = CoinConfiguration.query.filter_by(config_name='browser_login_bonus').first()
            if not browser_login:
                browser_config = CoinConfiguration(
                    config_name='browser_login_bonus',
                    coin_value=2,
                    description='Daily login bonus for browser users',
                    is_active=True
                )
                db.session.add(browser_config)
                print("✅ Browser login bonus configuration added!")

            # Mobile app login bonus
            app_login = CoinConfiguration.query.filter_by(config_name='app_login_bonus').first()
            if not app_login:
                app_config = CoinConfiguration(
                    config_name='app_login_bonus',
                    coin_value=5,
                    description='Daily login bonus for mobile app users',
                    is_active=True
                )
                db.session.add(app_config)
                print("✅ Mobile app login bonus configuration added!")

            # Ad watch reward (updated to 0.5)
            ad_reward = CoinConfiguration.query.filter_by(config_name='ad_watch_reward').first()
            if ad_reward:
                ad_reward.coin_value = 0.5
                ad_reward.description = 'Reward for watching 30-second ad session (3 ads)'
            else:
                ad_reward_config = CoinConfiguration(
                    config_name='ad_watch_reward',
                    coin_value=0.5,
                    description='Reward for watching 30-second ad session (3 ads)',
                    is_active=True
                )
                db.session.add(ad_reward_config)
            print("✅ Ad watch reward updated to 0.5 coins!")

            # Create AdNetwork table
            db.create_all()
            print("✅ AdNetwork table created!")

            db.session.commit()
            print("✅ All new configurations initialized successfully!")

        except Exception as e:
            print(f"❌ Error initializing configurations: {e}")
            db.session.rollback()

if __name__ == "__main__":
    init_new_configs()
from main import app, db, CoinConfiguration, AdNetwork

def initialize_new_system():
    """Initialize the new professional ad management system"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Update ad watch reward configuration for decimal support
            ad_reward_config = CoinConfiguration.query.filter_by(config_name='ad_watch_reward').first()
            if ad_reward_config:
                ad_reward_config.coin_value = 0.5
                ad_reward_config.description = 'Reward for watching complete ad sequence (browser users)'
            else:
                ad_reward_config = CoinConfiguration(
                    config_name='ad_watch_reward',
                    coin_value=0.5,
                    description='Reward for watching complete ad sequence (browser users)',
                    is_active=True
                )
                db.session.add(ad_reward_config)

            # Add webview reward configuration
            webview_reward_config = CoinConfiguration.query.filter_by(config_name='webview_ad_reward').first()
            if not webview_reward_config:
                webview_reward_config = CoinConfiguration(
                    config_name='webview_ad_reward',
                    coin_value=5.0,
                    description='Reward for watching complete ad sequence (webview app users)',
                    is_active=True
                )
                db.session.add(webview_reward_config)

            # Add ad sequence timing configuration
            sequence_timing_config = CoinConfiguration.query.filter_by(config_name='ad_sequence_duration').first()
            if not sequence_timing_config:
                sequence_timing_config = CoinConfiguration(
                    config_name='ad_sequence_duration',
                    coin_value=30,
                    description='Duration in seconds for complete ad sequence',
                    is_active=True
                )
                db.session.add(sequence_timing_config)

            # Add step delay configuration
            step_delay_config = CoinConfiguration.query.filter_by(config_name='ad_step_delay').first()
            if not step_delay_config:
                step_delay_config = CoinConfiguration(
                    config_name='ad_step_delay',
                    coin_value=4,
                    description='Delay in seconds between ad steps',
                    is_active=True
                )
                db.session.add(step_delay_config)

            db.session.commit()
            print("✅ New professional ad management system initialized successfully!")
            print("✅ All configurations updated for decimal coin support!")
            print("✅ Webview detection and rewards configured!")
            print("✅ Professional ad sequence system ready!")

        except Exception as e:
            print(f"❌ Error initializing new system: {e}")
            db.session.rollback()

if __name__ == "__main__":
    initialize_new_system()
