from pytest import raises
from dooit.api.exceptions import NoNodeError
from dooit.ui.api.widgets import TodoWidget
from dooit.ui.widgets.renderers.base_renderer import BaseRenderer
from tests.test_ui.ui_base import run_pilot, create_and_move_to_todo
from dooit.ui.tui import Dooit


def custom_formatter(value, todo):
    return "??"


async def test_todo_tree_focus():
    async with run_pilot() as pilot:
        app = pilot.app
        assert isinstance(app, Dooit)
        await create_and_move_to_todo(pilot)


async def test_todo_formatter():
    def get_formatted(renderer: BaseRenderer, attr: str):
        component = renderer._get_component(attr)
        formatter = renderer.tree.formatter
        return (
            getattr(formatter, attr)
            .format_value(component.model_value, component.model)
            .markup
        )

    async with run_pilot() as pilot:
        app = pilot.app
        assert isinstance(app, Dooit)

        tree = await create_and_move_to_todo(pilot)

        tree.add_sibling()
        await pilot.press(*list("nixos"))
        await pilot.press("escape")

        renderer = tree.current
        assert get_formatted(renderer, "description") == "nixos"

        app.api.formatter.todos.description.add(custom_formatter)
        assert get_formatted(renderer, "description") == "??"


async def test_no_node_error():
    async with run_pilot() as pilot:
        app = pilot.app
        assert isinstance(app, Dooit)

        tree = await create_and_move_to_todo(pilot)

        with raises(NoNodeError):
            tree.current


async def test_todo_tree_layout():
    async with run_pilot() as pilot:
        app = pilot.app
        assert isinstance(app, Dooit)

        tree = await create_and_move_to_todo(pilot)

        tree.add_sibling()
        await pilot.press(*list("nixos"))
        await pilot.press("escape")

        table = tree.current.make_renderable()
        assert table.columns[0].header == "status"

        app.api.layouts.todo_layout = [TodoWidget.description]
        table = tree.current.make_renderable()
        assert table.columns[0].header == "description"


async def test_incorrect_edit():
    async with run_pilot() as pilot:
        app = pilot.app
        assert isinstance(app, Dooit)

        tree = await create_and_move_to_todo(pilot)

        tree.add_sibling()
        await pilot.press(*list("nixos"))
        await pilot.press("escape")

        assert not tree.current.start_edit("incorrect")


async def test_remove_todo():
    async with run_pilot() as pilot:
        app = pilot.app
        assert isinstance(app, Dooit)

        tree = await create_and_move_to_todo(pilot)

        tree.add_sibling()
        await pilot.press(*list("nixos"))
        await pilot.press("escape")

        tree.remove_node()
        await pilot.pause()

        assert len(tree._options) == 1
        assert tree.highlighted == 0
        assert tree.current_model.description == "nixos"

        await pilot.press("y")
        assert len(tree._options) == 0
        assert tree.highlighted == None
