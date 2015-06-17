class Dashboard:
    widgets = []
    reports = []
    menu = None

    def register(self, class_obj):
        super(class_obj).register(self, class_obj)

    def get_urls(self):
        from django.conf.urls import url, include
        urlpatterns = []
        
        # get reports url
        for r in self.reports:
            urlpatterns += [
                url(r'reports/%s/' % r.get_slug(), include(r.urls)),
            ]

        return urlpatterns

#global dashboard object
_dashboard = Dashboard()

def register(obj):
    _dashboard.register(obj)
