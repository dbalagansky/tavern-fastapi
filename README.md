# tavern-fastapi
FastAPI plugin for Tavern testing framework

## How to use
1. Install with `pip install git+https://github.com/dbalagansky/tavern-fastapi.git@main`
2. Add the following lines to pyproject.toml` file.
```toml
[tool.pytest.ini_options]
tavern-http-backend = "fastapi"
```

## Credits
Based on [tavern-flask](https://github.com/taverntesting/tavern-flask) plugin by [@michaelboulton](https://github.com/michaelboulton) and original plugin for Tavern<2.0 by [@zaghaghi](https://github.com/zaghaghi).
