from __future__ import annotations


__all__ = ('session_logger', 'dispatcher_logger', 'runner_logger')


from logging import getLogger


session_logger = getLogger('funpaybotengine.session')
dispatcher_logger = getLogger('funpaybotengine.dispatcher')
runner_logger = getLogger('funpaybotengine.runner')
