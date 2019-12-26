"""
Create by yy on 2019/12/26
"""
from tool_yy import Helper

__all__ = ['create_helper']

from app.deploy.deploy import AutoDeploy


class HelperInstance(Helper):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def deploy(self):
        return AutoDeploy(self.init_db)


def create_helper():
    helper = HelperInstance()
    helper.config.from_object("app.config.app_config")
    return helper
