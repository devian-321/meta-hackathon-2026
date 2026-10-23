import pytest

from sample_app.pricing import total_cents


@pytest.mark.parametrize(
    ("price", "quantity", "discount", "expected"),
    [(1000, 2, 0, 2000), (1000, 2, 10, 1800), (999, 1, 15, 849), (500, 3, 100, 0)],
)
def test_invoice_total(price: int, quantity: int, discount: int, expected: int) -> None:
    assert total_cents(price, quantity, discount) == expected


@pytest.mark.parametrize(
    ("price", "quantity", "discount"), [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101)]
)
def test_invalid_invoice(price: int, quantity: int, discount: int) -> None:
    with pytest.raises(ValueError):
        total_cents(price, quantity, discount)
