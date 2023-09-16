import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
from platform import python_version

def check_python_version():
    print('Your python version is ', python_version())
    assert python_version()[:3] >= '3.7', 'Make sure you use python version >=3.7'

def check_env_setup():
    dependencies = open("requirements.txt").readlines()
    try:
        pkg_resources.require(dependencies)
        print("✅ ALL GOOD")
    except DistributionNotFound as e:
        print("⚠️ Library is missing")
        print(e)
    except VersionConflict as e:
        print("⚠️ Library version conflict")
        print(e)
    except Exception as e:
        print("⚠️ Something went wrong")
        print(e)

if __name__ == '__main__':
    check_python_version()
    check_env_setup()