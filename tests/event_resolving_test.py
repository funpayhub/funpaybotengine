from __future__ import annotations

import pytest
from funpaybotengine import Bot
from funpaybotengine.types import OrderType, UserBadge
from funpaybotengine.types.messages import Message, MessageMeta, MessageType
from funpaybotengine.dispatching.events import builtin_events as e
from funpaybotengine.runner.event_collector import MsgUpdate


@pytest.fixture(scope='module')
def message() -> Message:
    return Message(
        raw_source='',
        id=1,
        is_heading=True,
        sender_id=0,
        sender_username='',
        badge=UserBadge(raw_source='', text='', css_class=''),
        send_date_text='01.01.2001',
        text='',
        image_url=None,
        chat_id=12345,
        chat_name='',
        meta=MessageMeta(
            raw_source='', type=MessageType.NEW_ORDER, order_id='ABCDEFGH', buyer_id=12345
        ),
    )


@pytest.fixture(scope='module')
def bot() -> Bot:
    bot = Bot('golden_key')
    bot._userid = 12345
    return bot


@pytest.mark.parametrize(
    ['meta', 'related_type'],
    (
        [MessageMeta(type=MessageType.NEW_ORDER, buyer_id=12345), OrderType.PURCHASE],
        [MessageMeta(type=MessageType.NEW_ORDER, buyer_id=12346), OrderType.SALE],
        [MessageMeta(type=MessageType.ORDER_CLOSED, buyer_id=12345), OrderType.PURCHASE],
        [MessageMeta(type=MessageType.ORDER_CLOSED, buyer_id=12346), OrderType.SALE],
        [MessageMeta(type=MessageType.ORDER_REFUNDED), OrderType.UNKNOWN],
        [MessageMeta(type=MessageType.ORDER_PARTIALLY_REFUNDED), OrderType.UNKNOWN],
        [MessageMeta(type=MessageType.ORDER_CLOSED_BY_ADMIN), OrderType.UNKNOWN],
        [MessageMeta(type=MessageType.ORDER_REOPENED), OrderType.UNKNOWN],
    ),
)
def test_order_relation(bot: Bot, message: Message, meta: MessageMeta, related_type: OrderType):
    message.meta = meta
    upd = MsgUpdate(e.NewMessage(object=message, tag='').as_(bot))
    assert upd.related_type is related_type


@pytest.mark.parametrize(
    ['meta', 'event_type'],
    [
        [MessageMeta(type=MessageType.NEW_FEEDBACK), e.NewReview],
        [MessageMeta(type=MessageType.NEW_FEEDBACK_REPLY), e.NewReviewReply],
        [MessageMeta(type=MessageType.FEEDBACK_CHANGED), e.ReviewChanged],
        [MessageMeta(type=MessageType.FEEDBACK_REPLY_CHANGED), e.ReviewReplyChanged],
        [MessageMeta(type=MessageType.FEEDBACK_DELETED), e.ReviewDeleted],
        [MessageMeta(type=MessageType.FEEDBACK_REPLY_DELETED), e.ReviewReplyDeleted],
    ],
)
def test_review_relation(bot: Bot, message: Message, meta: MessageMeta, event_type: e.ReviewEvent):
    message.meta = meta
    upd = MsgUpdate(e.NewMessage(object=message, tag='').as_(bot))
    assert type(upd.event) is event_type
