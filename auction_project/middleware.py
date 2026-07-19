import re


class AdminStyleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/admin/') and response.status_code == 200:
            content = response.content.decode('utf-8', errors='ignore')
            if '</head>' in content:
                admin_css = '''
<style>
:root {
  --ah-primary: #111111;
  --ah-primary-dark: #000000;
  --ah-accent: #333333;
  --ah-gradient: linear-gradient(135deg, #111111 0%, #333333 50%, #555555 100%);
}
#header {
  background: var(--ah-gradient) !important;
  border-bottom: none !important;
}
#header a:link, #header a:visited { color: #fff !important; }
#branding h1 { font-weight: 700 !important; letter-spacing: 0.5px; }
#branding h1 a { color: #fff !important; }
#user-tools a, #user-tools span { color: #cccccc !important; }
#user-tools a:hover { color: #fff !important; }
#nav-sidebar {
  background: #f8f8f8 !important;
  border-right: 1px solid #e0e0e0 !important;
}
#nav-sidebar .module a { color: #111 !important; }
#nav-sidebar .module a:hover {
  color: #000 !important;
  background: #e8e8e8 !important;
}
#nav-sidebar .module h3 {
  color: #111 !important;
  font-weight: 600;
}
#content { background: #fafafa !important; }
div.breadcrumbs {
  background: var(--ah-primary) !important;
  color: #fff !important;
  border-radius: 6px;
  margin: 10px 0;
}
div.breadcrumbs a { color: #cccccc !important; }
.module {
  border-radius: 8px !important;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  border: 1px solid #e0e0e0 !important;
}
.module caption {
  background: var(--ah-gradient) !important;
  color: #fff !important;
  font-weight: 600;
  padding: 10px 14px;
}
.button, input[type="submit"], input[type="button"], .submit-row input {
  background: var(--ah-primary) !important;
  border-color: var(--ah-primary-dark) !important;
  border-radius: 5px !important;
  font-weight: 500;
}
.button:hover, input[type="submit"]:hover, input[type="button"]:hover {
  background: var(--ah-primary-dark) !important;
}
.object-tools { margin-bottom: 10px; }
.object-tools a {
  background: var(--ah-accent) !important;
  border-radius: 5px !important;
  font-weight: 500;
}
.object-tools a:hover { background: var(--ah-primary-dark) !important; }
#content-main .results {
  border-radius: 8px;
  overflow: hidden;
}
table.results th {
  background: #f0f0f0 !important;
  color: #111 !important;
  font-weight: 600;
}
table.results tr:hover td { background: #e8e8e8 !important; }
</style>
'''
                content = content.replace('</head>', admin_css + '</head>')
                response.content = content.encode('utf-8')
        return response
