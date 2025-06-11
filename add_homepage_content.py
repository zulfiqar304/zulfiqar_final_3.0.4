
from main import app, db, HomePageContent

def add_homepage_content_table():
    """Add home page content table and default data"""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            
            # Add default hero content
            existing_hero = HomePageContent.query.filter_by(section_type='hero').first()
            if not existing_hero:
                default_hero = HomePageContent(
                    section_type='hero',
                    title='Welcome to ZMWORLD',
                    subtitle='Your one-stop destination for social media services',
                    description='',
                    display_order=0
                )
                db.session.add(default_hero)
            
            # Add default feature content
            existing_features = HomePageContent.query.filter_by(section_type='feature').count()
            if existing_features == 0:
                features = [
                    {
                        'title': 'Social Media Growth',
                        'description': 'Boost your social media presence with our premium services',
                        'display_order': 1
                    },
                    {
                        'title': 'Instant Delivery',
                        'description': 'Fast and reliable service delivery for all your orders',
                        'display_order': 2
                    },
                    {
                        'title': 'Secure Platform',
                        'description': 'Safe and secure transactions with email verification',
                        'display_order': 3
                    }
                ]
                
                for feature_data in features:
                    feature = HomePageContent(
                        section_type='feature',
                        title=feature_data['title'],
                        description=feature_data['description'],
                        display_order=feature_data['display_order']
                    )
                    db.session.add(feature)
            
            db.session.commit()
            print("✅ Home page content table created successfully!")
            print("✅ Default content added!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_homepage_content_table()
