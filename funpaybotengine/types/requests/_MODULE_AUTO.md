# requests/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## runner.py
```
__all__ = …

cls RequestableObject(ABC, BaseModel)
  # Base class for all objects that can be sent as runner requests.
  type() -> str
  async as_data_dict(bot: Bot) -> dict[str, Any]

cls OrdersCountersRequestObject(RequestableObject, BaseModel)
  # Request for retrieving order counters of a specific user.
  type() -> str
  data() -> bool
  async as_data_dict(bot: Bot) -> dict[str, Any]

cls ChatCounterRequestObject(RequestableObject, BaseModel)
  # Request for retrieving chat counter for a user.
  type() -> str
  data() -> bool
  async as_data_dict(bot: Bot) -> dict[str, Any]

cls CPURequestObject(RequestableObject, BaseModel)
  # Request for information about the offer currently being viewed by a user.
  type() -> str
  data() -> bool

cls ChatBookmarksRequestObject(RequestableObject, BaseModel)
  # Request for retrieving chat bookmarks for a user.
  type() -> str
  async as_data_dict(bot: Bot) -> dict[str, Any]

cls RequestNodeInfo(BaseModel)
  # Chat node metadata used in ``NodeRequestObject.data``.
  content() -> str

cls NodeRequestObject(RequestableObject, BaseModel)
  # Request for retrieving chat (node) message history.
  type() -> str

cls Action(ABC, BaseModel)
  # Base class for all runner actions.
  action() -> str

cls SendingMessageData(BaseModel)
  # Chat node metadata used in ``SendMessageAction.message_data``.

cls SendMessageAction(Action, BaseModel)
  # Action that sends a message to a chat.
  action() -> str

```
