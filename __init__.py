from flask_assets import Environment
from webassets.loaders import PythonLoader as PythonAssetsLoader
import assets


assets_env = Environment(app)
assets_loader = PythonAssetsLoader(assets)
for name, bundle in assets_loader.load_bundles().iteritems():
    assets_env.register(name, bundle)

    