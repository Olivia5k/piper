import pytest

from piper.agent import Agent
from piper.config import AgentConfig
from mock import Mock


@pytest.fixture
def agent():
    config = AgentConfig()
    agent = Agent(config)
    agent.db = Mock()

    return agent


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
