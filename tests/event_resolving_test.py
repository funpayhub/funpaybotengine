from funpaybotengine import Bot
from funpaybotengine.dispatching import NewMessage
from funpaybotengine.runner.event_collector import MsgUpdate
from funpaybotengine.types.messages import Message, MessageType, MessageMeta
from funpaybotengine.types import  UserBadge, OrderType
import pytest


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
            raw_source='',
            type=MessageType.NEW_ORDER,
            order_id='ABCDEFGH',
            buyer_id=12345
        )
)

@pytest.fixture(scope='module')
def bot() -> Bot:
    bot = Bot('golden_key')
    bot._userid = 12345
    return bot


@pytest.mark.parametrize(
    ['meta', 'related_type'],
    (
        [
            MessageMeta(raw_source='', type=MessageType.NEW_ORDER, buyer_id=12345),
            OrderType.PURCHASE,
        ],
        [
            MessageMeta(raw_source='', type=MessageType.NEW_ORDER, buyer_id=12346),
            OrderType.SALE
        ],
        [
            MessageMeta(raw_source='', type=MessageType.ORDER_CLOSED, buyer_id=12345),
            OrderType.PURCHASE
        ],
        [
            MessageMeta(raw_source='', type=MessageType.ORDER_CLOSED, buyer_id=12346),
            OrderType.SALE
        ],
        [
            MessageMeta(raw_source='', type=MessageType.ORDER_REFUNDED),
            OrderType.UNKNOWN
        ],
        [
            MessageMeta(raw_source='', type=MessageType.ORDER_PARTIALLY_REFUNDED),
            OrderType.UNKNOWN
        ],
        [
            MessageMeta(raw_source='', type=MessageType.ORDER_CLOSED_BY_ADMIN),
            OrderType.UNKNOWN
        ],
        [
            MessageMeta(raw_source='', type=MessageType.ORDER_REOPENED),
            OrderType.UNKNOWN
        ]
    )
)
def test_relation(bot: Bot, message: Message, meta: MessageMeta, related_type: OrderType):
    message.meta = meta
    upd = MsgUpdate(NewMessage(object=message, tag='').as_(bot))
    assert upd.related_type is related_type
