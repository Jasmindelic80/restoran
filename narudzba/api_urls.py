from rest_framework import routers
from .api_views import NarudzbaViewSet, StavkaNarudzbeViewSet, StavkaViewSet

router = routers.DefaultRouter()
router.register(r'narudzbe', NarudzbaViewSet)
router.register(r'stavke_narudzbe', StavkaNarudzbeViewSet)
router.register(r'stavke', StavkaViewSet)

urlpatterns = router.urls
