from setuptools import setup, find_namespace_packages

setup(
    name="twitter_ai_agent",
    version="0.1.0",
    packages=find_namespace_packages(include=["src*"]),
    package_dir={"": "."},
    include_package_data=True,
    package_data={
        "src": ["data/*.json"],
    },
    install_requires=[
        "streamlit",
        "tweepy",
        "openai",
        "python-dotenv",
        "plotly",
        "pandas"
    ],
) 