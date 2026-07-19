from django.contrib.admin import AdminSite


class AuctionHubAdminSite(AdminSite):
    site_header = 'AuctionHub Administration'
    site_title = 'AuctionHub Admin Portal'
    index_title = 'Welcome to AuctionHub Admin'
    site_url = '/'


admin_site = AuctionHubAdminSite(name='admin')
