from app import main
from config import ProductionConfig

application = main(ProductionConfig)

if __name__ == "__main__":
    application.run()
