from dataclasses import dataclass, field

import sqlglot


@dataclass(kw_only=True)
class SqlViewGenerator:
    """A class to generate SQL view statements given a select
    statement or subquery.

    Generated SQL is compatible with mysql, postgres and sqlite3.

    The given `subquery` is not validated.

    For use with view definitions.
    """

    report_model: str = None
    ordering: list[str] | None = field(default_factory=list)
    order_by: str | None = field(init=False, default=None)
    with_stmt: str | None = field(default="")
    footer: str = field(init=False, default=None)
    template: str | None = field(
        default="{with_stmt} {select_stmt} from ({subquery}) as A ORDER BY {order_by};"
    )

    def __post_init__(self):
        ordering = [f"{fld[1:]} desc" if fld.startswith("~") else fld for fld in self.ordering]
        self.order_by = ", ".join(ordering) or "subject_identifier"
        self.footer = f") as A ORDER BY {self.order_by}"

    @staticmethod
    def transpile(sql: str, read: str | None = None, write: str = None) -> str:
        read = read or "mysql"
        sql = sql.replace(";", "")
        return sqlglot.transpile(sql, read=read, write=write)[0]

    def as_mysql(self, subquery: str, read: str | None = None) -> str:
        select_stmt = f"select *, uuid() as id, now() as `created`, '{self.report_model}' as `report_model`"  # noqa
        subquery = self.transpile(subquery, read=read, write="mysql")
        return self.template.format(
            with_stmt=self.with_stmt,
            select_stmt=select_stmt,
            subquery=subquery,
            order_by=self.order_by,
        )

    def as_postgres(self, subquery: str, read: str | None = None) -> str:
        select_stmt = f"select *, get_random_uuid() as id, now() as created, '{self.report_model}' as report_model"  # noqa
        subquery = self.transpile(subquery, read=read, write="postgres")
        return self.template.format(
            with_stmt=self.with_stmt,
            select_stmt=select_stmt,
            subquery=subquery,
            order_by=self.order_by,
        )

    def as_sqlite(self, subquery: str, read: str | None = None) -> str:
        """For UUID support in sqlite, install sqlite/uuid.
        See https://github.com/nalgeon/sqlpkg-cli?tab=readme-ov-file
        and https://sqlpkg.org/?q=uuid

            $ curl -sS https://webi.sh/sqlpkg | sh
            $ sqlpkg install sqlite/uuid
        """
        select_stmt = f"select *, uuid() as id, datetime() as created, '{self.report_model}' as report_model"  # noqa
        subquery = self.transpile(subquery, read=read, write="sqlite")
        return self.template.format(
            with_stmt=self.with_stmt,
            select_stmt=select_stmt,
            subquery=subquery,
            order_by=self.order_by,
        )
