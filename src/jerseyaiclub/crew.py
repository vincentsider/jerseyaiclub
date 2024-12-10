from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
import yaml
import os

# Instantiate tools
search_tool = SerperDevTool()

@CrewBase
class Jerseyaiclub():
    """Jerseyaiclub crew"""

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'config', 'agents.yaml'), 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open(os.path.join(current_dir, 'config', 'tasks.yaml'), 'r') as f:
            self.tasks_config = yaml.safe_load(f)

    @agent
    def sector_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['sector_analysis_agent'],
            verbose=True,
            tools=[search_tool],
            llm_provider_model="gpt-4o",
            temperature=0.1,
            max_iter=5
        )

    @agent
    def process_mapping_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['process_mapping_agent'],
            verbose=True,
            llm_provider_model="gpt-4o",
            temperature=0.1,
            max_iter=5
        )

    @agent
    def workflow_discovery_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['workflow_discovery_agent'],
            verbose=True,
            llm_provider_model="gpt-4o",
            temperature=0.1,
            max_iter=5
        )

    @agent
    def agent_matching_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['agent_matching_agent'],
            verbose=True,
            llm_provider_model="gpt-4o",
            temperature=0.1,
            max_iter=5
        )

    @task
    def sector_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['sector_analysis_task'],
            agent=self.sector_analysis_agent()
        )

    @task
    def process_mapping_task(self) -> Task:
        return Task(
            config=self.tasks_config['process_mapping_task'],
            agent=self.process_mapping_agent(),
            async_execution=True,
            context_from_tasks=[self.sector_analysis_task()]
        )

    @task
    def workflow_redesign_task(self) -> Task:
        return Task(
            config=self.tasks_config['workflow_redesign_task'],
            agent=self.workflow_discovery_agent(),
            context_from_tasks=[self.process_mapping_task()]
        )

    @task
    def agent_definition_task(self) -> Task:
        return Task(
            config=self.tasks_config['agent_definition_task'],
            agent=self.agent_matching_agent(),
            context_from_tasks=[self.workflow_redesign_task()]
        )

    @task
    def output_compilation_task(self) -> Task:
        return Task(
            config=self.tasks_config['output_compilation_task'],
            agent=self.sector_analysis_agent(),
            context_from_tasks=[
                self.process_mapping_task(),
                self.workflow_redesign_task(),
                self.agent_definition_task()
            ],
            output_file="workflow_report.md"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Workflow Discovery Crew"""
        return Crew(
            agents=[
                self.sector_analysis_agent(),
                self.process_mapping_agent(),
                self.workflow_discovery_agent(),
                self.agent_matching_agent()
            ],
            tasks=[
                self.sector_analysis_task(),
                self.process_mapping_task(),
                self.workflow_redesign_task(),
                self.agent_definition_task(),
                self.output_compilation_task()
            ],
            process=Process.hierarchical,
            memory=True,
            cache=True,
            max_rpm=1000,
            verbose=True,
            #manager_agent=self.sector_analysis_agent(),

            manager_llm="gpt-4o"
        )
