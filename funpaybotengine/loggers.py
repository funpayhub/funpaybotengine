from __future__ import annotations


__all__ = (
    'session_logger',
    'router_logger',
    'dispatcher_logger',
    'runner_logger',
    'methods_logger',
)


from logging import getLogger


methods_logger = getLogger('funpaybotengine.methods')
"""What a method could not make sense of.

Separate from ``session_logger``: the session reports transport, a method
reports the answer's shape. Turning one up to DEBUG should not turn on the
other -- a response nobody could parse is a different question from a request
that never arrived.
"""

session_logger = getLogger('funpaybotengine.session')
router_logger = getLogger('funpaybotengine.router')
dispatcher_logger = getLogger('funpaybotengine.dispatcher')
runner_logger = getLogger('funpaybotengine.runner')
