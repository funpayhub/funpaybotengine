# pages/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## base.py
```
__all__ = ('FunPayPage',)

cls FunPayPage(FunPayObject, BaseModel)
  # Base class for FunPay pages.

```

## chat_page.py
```
__all__ = ('ChatPage',)

cls ChatPage(FunPayPage, BaseModel)
  # Represents a chat page (`https://funpay.com/chat/?node=<chat_id>`).

```

## main_page.py
```
__all__ = ('MainPage',)

cls MainPage(FunPayPage, BaseModel)
  # Represents the main page (https://funpay.com).

```

## my_chips_page.py
```
__all__ = ('MyChipsPage',)

cls MyChipsPage(FunPayPage)
  # Represents personal chips page (`/chips/<subcategory_id>/trade`).

```

## my_offers_page.py
```
__all__ = ('MyOffersPage',)

cls MyOffersPage(FunPayPage)
  # Represents personal lots page (`/lots/<subcategory_id>/trade`).

```

## offer_page.py
```
__all__ = ('OfferPage',)

cls OfferPage(FunPayPage)

```

## order_page.py
```
__all__ = ('OrderPage',)

cls OrderPage(FunPayPage, BaseModel)
  # Represents an order page (`https://funpay.com/orders/<order_id>/`).
  short_description() -> str | None
    # Order short description (title).
  full_description() -> str | None
    # Order full description (detailed description).
  amount() -> int | None
  open_date_text() -> str | None
    # Order open date.
  close_date_text() -> str | None
    # Order close date.
  order_category_name() -> str | None
    # Order category name.
  order_subcategory_name() -> str | None
    # Order subcategory name.
  order_total() -> MoneyValue | None
    # Order total.

```

## profile_page.py
```
__all__ = ('ProfilePage',)

cls ProfilePage(FunPayPage, BaseModel)
  # Represents a user profile page (`https://funpay.com/users/<user_id>`).

```

## settings_page.py
```
__all__ = ('SettingsPage',)

cls SettingsPage(FunPayPage): settings: Settings
  # Represents user settings page (``https://funpay.com/account/settings``).

```

## sras_info_page.py
```
__all__ = ('SrasInfoPage',)

cls SrasInfoPage(FunPayPage)
  # Represents the SRAS info page (``https://funpay.com/sras/info``).

```

## subcategory_page.py
```
__all__ = ('SubcategoryPage',)

cls SubcategoryPage(FunPayPage, BaseModel)
  # Represents a subcategory offers list page

```

## transactions_page.py
```
__all__ = ('TransactionsPage',)

cls TransactionsPage(FunPayPage, BaseModel)
  # Represents the transactions page (https://funpay.com/account/balance).

```
