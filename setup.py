from setuptools import find_packages, setup

package_name = 'science'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    include_package_data = True,

    # "data_files" are needed when using python to install things
    # but we are mostly using cmake and it already does that.
    # If left uncommented, it will ALSO install stuff and can cause issues
    #
    # data_files=[
    #     ('share/ament_index/resource_index/packages',
    #         ['resource/' + package_name]),
    #     ('share/' + package_name, ['package.xml']),
    # ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rsx-science',
    maintainer_email='thy_mother@pp.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'tester = science.pub_image:main',
            'subscriber = science.sub:main',
            'hello = science.hello_science:main',
            'gui_test = science.science_test:main', 
        ],
    },
)
