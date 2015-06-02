import pytest
from mock import Mock
from mock import patch

from piper import utils
from piper.agent import Agent
from piper.config import AgentConfig


@pytest.fixture
def agent():
    config = AgentConfig()
    agent = Agent(config)
    agent.id = 'maiden-voyage'
    agent.db = Mock()

    return agent


@pytest.fixture
def deleted_change():
    change = {
        'old_val': {
            'id': 'uuid'
        },
        'new_val': None,
    }
    return change


@pytest.fixture
def started_change():
    change = {
        'old_val': None,
        'new_val': {
            'id': 'alice-in-videoland',
            'started': utils.now(),
            'eligible_agents': ['maiden-voyage']
        },
    }
    return change


@pytest.fixture
def nonapplicable_change():
    change = {
        'old_val': None,
        'new_val': {
            'id': 'alice-in-videoland',
            'eligible_agents': []
        },
    }
    return change


@pytest.fixture
def applicable_change():
    change = {
        'old_val': None,
        'new_val': {
            'id': 'alice-in-videoland',
            'eligible_agents': [
                'maiden-voyage',
            ]
        },
    }
    return change

@pytest.fixture
def config():
    config = {
        'id': 'bailando'
    }
    return config


class TestAgentListen:
    def test_feed_handles_incoming(self, agent):
        agent.handle = Mock()
        change = Mock()
        agent.db.build.feed = Mock(return_value=[change])

        agent.listen()

        agent.handle.assert_called_once_with(change)

    @pytest.mark.randomize(length=int, ncalls=10, min_num=0, max_num=100)
    def test_feed_handles_all_items(self, agent, length):
        agent.handle = Mock()
        changes = [Mock() for x in range(length)]
        agent.db.build.feed = Mock(return_value=changes)

        agent.listen()

        assert agent.handle.call_count == length


class TestAgentHandle:
    def test_deleted_item(self, agent, deleted_change):
        ret = agent.handle(deleted_change)

        assert ret is False

    def test_already_started_item(self, agent, started_change):
        ret = agent.handle(started_change)

        assert ret is None

    def test_not_eligible_to_build(self, agent, nonapplicable_change):
        ret = agent.handle(nonapplicable_change)

        assert ret is None

    def test_passing(self, agent, applicable_change):
        agent.build = Mock()
        ret = agent.handle(applicable_change)

        assert ret is agent.build.return_value
        agent.build.assert_called_once_with(applicable_change['new_val'])


class TestAgentBuild:
    @patch('piper.agent.Build')
    def test_busy_setting(self, build, agent, config):
        agent.update = Mock()
        agent.build(config)

        # One to lock, one to unlock.
        assert agent.update.call_count == 2

    @patch('piper.agent.Build')
    def test_busy_exception_handling(self, build, agent, config):
        agent.update = Mock()
        agent.log = Mock()
        build.side_effect = Exception()

        agent.build(config)

        # It's inherently silly to mock logging, but in this case we actually
        # want to make sure that the logging is logging the exception.
        agent.log.exception.assert_called_once_with(
            'Build threw internal exception'
        )

        assert agent.update.call_count == 2
        assert agent.building is None

    @patch('piper.agent.Build')
    def test_build_calls(self, build, agent, config):
        agent.update = Mock()
        agent.build(config)

        build.assert_called_once_with(config)
        build.return_value.run.assert_called_once_with()


class TestAgentProperties:
    @patch('json.loads')
    @patch('piper.agent.oneshot')
    def test_calls(self, oneshot, loads, agent):
        ret = agent.properties

        oneshot.assert_called_once_with('facter --json')
        loads.assert_called_once_with(oneshot.return_value)

        assert ret is loads.return_value
        assert agent._properties is ret


class TestAgentUpdate:
    def test_send(self, agent):
        agent.as_dict = Mock()
        agent.update()

        agent.db.agent.update.assert_called_once_with(
            agent.as_dict.return_value
        )
