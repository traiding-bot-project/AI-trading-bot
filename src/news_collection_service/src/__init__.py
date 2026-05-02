"""Root module for the News Collection microservice."""

from src.settings import settings

if __name__ == "__main__":
    print(settings.datasource.pl.pap.available_categories) 
