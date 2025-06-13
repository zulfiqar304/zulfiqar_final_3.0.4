
from main import app, db, CoinConfiguration

def add_coin_purchase_config():
    """Add PKR to coins rate configuration and EasyPaisa account details"""
    with app.app_context():
        try:
            # Check if config already exists
            existing_config = CoinConfiguration.query.filter_by(config_name='pkr_to_coins_rate').first()
            if not existing_config:
                config = CoinConfiguration(
                    config_name='pkr_to_coins_rate',
                    coin_value=2,  # 2 PKR = 1 Coin
                    description='Pakistani Rupees to coins conversion rate (PKR per coin)',
                    is_active=True
                )
                db.session.add(config)
                print("✅ PKR to coins rate configuration added successfully!")
            else:
                print("✅ PKR to coins rate configuration already exists!")

            # Add EasyPaisa account name configuration
            existing_name = CoinConfiguration.query.filter_by(config_name='easypaisa_account_name').first()
            if not existing_name:
                name_config = CoinConfiguration(
                    config_name='easypaisa_account_name',
                    coin_value=0,  # Not used for text configs
                    description='Zulfiqar Ali',  # Store name in description field
                    is_active=True
                )
                db.session.add(name_config)
                print("✅ EasyPaisa account name configuration added successfully!")
            else:
                print("✅ EasyPaisa account name configuration already exists!")

            # Add EasyPaisa account number configuration
            existing_number = CoinConfiguration.query.filter_by(config_name='easypaisa_account_number').first()
            if not existing_number:
                number_config = CoinConfiguration(
                    config_name='easypaisa_account_number',
                    coin_value=0,  # Not used for text configs
                    description='+92-343-3662304',  # Store number in description field
                    is_active=True
                )
                db.session.add(number_config)
                print("✅ EasyPaisa account number configuration added successfully!")
            else:
                print("✅ EasyPaisa account number configuration already exists!")
                
            db.session.commit()
                
        except Exception as e:
            print(f"❌ Error adding configuration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_coin_purchase_config()
