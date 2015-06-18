import uuid
import pytest
from mock import Mock
from mock import patch

from piper import utils
from piper.agent import Agent
from piper.agent import AgentAPI
from piper.agent import AgentCLI
from piper.config import AgentConfig


@pytest.fixture
def agent():
    config = AgentConfig().load()
    agent = Agent(config)
    agent.id = 'maiden-voyage'
    agent.db = Mock()

    return agent


@pytest.fixture
def nobuild_agent():
    a = agent()
    a.build = Mock()
    return a


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
            'config': {
                'started': utils.now(),
                'eligible_agents': ['maiden-voyage']
            },
        },
    }
    return change


@pytest.fixture
def nonapplicable_change():
    change = {
        'old_val': None,
        'new_val': {
            'id': 'alice-in-videoland',
            'config': {
                'eligible_agents': [],
            },
        },
    }
    return change


@pytest.fixture
def applicable_change():
    change = {
        'old_val': None,
        'new_val': {
            'id': 'alice-in-videoland',
            'config': {
                'eligible_agents': [
                    'maiden-voyage',
                ],
            },
        },
    }
    return change


@pytest.fixture
def config():
    config = {
        'id': 'bailando'
    }
    return config


@pytest.fixture
def build_id():
    return uuid.uuid4()


@pytest.fixture
def cli():
    config = AgentConfig().load()
    return AgentCLI(config)


@pytest.fixture
def ns():
    return Mock()


@pytest.fixture
def api_request():
    return Mock()


@pytest.fixture
def api():
    config = AgentConfig()
    api = AgentAPI(config)
    api.db = Mock()

    return api


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
    def test_deleted_item(self, nobuild_agent, deleted_change):
        ret = nobuild_agent.handle(deleted_change)

        assert ret is False

    def test_already_started_item(self, nobuild_agent, started_change):
        ret = nobuild_agent.handle(started_change)

        assert ret is None

    @pytest.mark.skipif(True, reason='eligibility disabled')
    def test_not_eligible_to_build(self, nobuild_agent, nonapplicable_change):
        ret = nobuild_agent.handle(nonapplicable_change)

        assert ret is None

    def test_passing(self, nobuild_agent, applicable_change):
        nobuild_agent.build = Mock()
        ret = nobuild_agent.handle(applicable_change)

        assert ret is nobuild_agent.build.return_value
        nobuild_agent.build.assert_called_once_with(
            applicable_change['new_val']['id'],
            applicable_change['new_val']['config']
        )


class TestAgentBuild:
    @patch('piper.agent.Build')
    def test_busy_setting(self, build, agent, build_id, config):
        agent.update = Mock()
        agent.build(build_id, config)

        # One to lock, one to unlock.
        assert agent.update.call_count == 2

    @patch('piper.agent.Build')
    def test_busy_exception_handling(self, build, agent, config):
        agent.update = Mock()
        agent.log = Mock()
        build.side_effect = Exception()

        agent.build(build_id, config)

        # It's inherently silly to mock logging, but in this case we actually
        # want to make sure that the logging is logging the exception.
        agent.log.exception.assert_called_once_with(
            'Build threw internal exception'
        )

        assert agent.update.call_count == 2
        assert agent.building is None

    @patch('piper.agent.BuildConfig')
    @patch('piper.agent.Build')
    def test_build_calls(self, build, buildconfig, agent, config):
        agent.update = Mock()
        agent.build(build_id, config)

        load = buildconfig.return_value.load.return_value
        build.assert_called_once_with(load)
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


class TestAgentRegister(object):
    def test_already_registered(self, agent):
        agent.register()

        agent.db.agent.get.assert_called_once_with(agent.id)
        assert agent.db.agent.add.call_count == 0

    def test_not_registered(self, agent):
        agent.db.agent.get.return_value = None
        agent.register()

        agent.db.agent.get.assert_called_once_with(agent.id)
        assert agent.db.agent.add.call_count == 1


class TestAgentCliRun(object):
    def test_without_argument(self, cli, ns):
        ns.agent_command = None
        cli.agent.listen = Mock()
        cli.run(ns)

        cli.agent.listen.assert_called_once_with()

    def test_with_start_argument(self, cli, ns):
        ns.agent_command = 'start'
        cli.agent.listen = Mock()
        cli.run(ns)

        cli.agent.listen.assert_called_once_with()


class TestAgentApiGet(object):
    def test_existing_agent(self, api, api_request):
        agent = Mock()
        api.db.agent.get.return_value = agent

        ret = api.get(api_request)

        assert ret is agent
        api.db.agent.get.assert_called_once_with(
            api_request.match_info.get.return_value
        )

    def test_nonexisting_agent(self, api, api_request):
        api.db.agent.get.return_value = None

        ret = api.get(api_request)
        assert ret == ({}, 404)
