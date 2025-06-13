
from main import app, db, AdLink, MultipleAdConfig

def add_profitable_rate_ad():
    """Add Profitable Rate CPM ad configuration"""
    with app.app_context():
        try:
            # Add as an ad link for direct ads
            existing_link = AdLink.query.filter_by(name='Profitable Rate CPM').first()
            if not existing_link:
                new_ad_link = AdLink(
                    name='Profitable Rate CPM',
                    ad_url='https://www.profitableratecpm.com/zpwh13266?key=c4d74020b7b9f9a8efa590f59a34603b',
                    display_order=1,
                    is_active=True
                )
                db.session.add(new_ad_link)
                print("✅ Profitable Rate CPM ad link added successfully!")
            else:
                print("✅ Profitable Rate CPM ad link already exists!")

            # Also add as a multiple ad config for watch_ad_2
            existing_config = MultipleAdConfig.query.filter_by(ad_name='Profitable Rate CPM').first()
            if not existing_config:
                # Create ad code that opens the URL in a new window
                ad_code = f'''
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
    <h3 style="margin: 0 0 15px 0;">💰 Profitable Rate CPM</h3>
    <p style="margin: 0 0 20px 0;">Click to visit high-paying ads!</p>
    <a href="https://www.profitableratecpm.com/zpwh13266?key=c4d74020b7b9f9a8efa590f59a34603b" 
       target="_blank" 
       style="display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
        Visit Now
    </a>
</div>
<script>
setTimeout(function() {{
    window.open("https://www.profitableratecpm.com/zpwh13266?key=c4d74020b7b9f9a8efa590f59a34603b", "_blank");
}}, 2000);
</script>
'''
                
                new_multiple_ad = MultipleAdConfig(
                    ad_type='watch_ad_2',
                    ad_name='Profitable Rate CPM',
                    ad_code=ad_code,
                    display_order=1,
                    is_active=True
                )
                db.session.add(new_multiple_ad)
                print("✅ Profitable Rate CPM multiple ad configuration added successfully!")
            else:
                print("✅ Profitable Rate CPM multiple ad configuration already exists!")

            db.session.commit()
            print("🎉 All Profitable Rate CPM configurations added successfully!")
                
        except Exception as e:
            print(f"❌ Error adding Profitable Rate CPM configurations: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_profitable_rate_ad()
