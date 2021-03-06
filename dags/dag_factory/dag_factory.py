import os

from dag_factory.components.NewsCrawler import NewsCrawler
from dag_factory.components.MongoImport import MongoImport
from dag_factory.components.NewsCleaner import NewsCleaner

from tfx.orchestration import metadata
from tfx.orchestration import pipeline

from tfx.orchestration.airflow.airflow_dag_runner import AirflowDagRunner
from tfx.orchestration.airflow.airflow_dag_runner import AirflowPipelineConfig


def create_dag(name, url, airflow_config, output_dir="/output"):
    pipeline_name = name
    pipeline_root = os.path.join(output_dir, 'pipelines', pipeline_name)
    metadata_path = os.path.join(output_dir, 'metadata', pipeline_name,
                                 'metadata.db')

    crawler = NewsCrawler(url=url)
    cleaner = NewsCleaner(rss_feed=crawler.outputs["rss_feed"])
    mongo = MongoImport(rss_feed=cleaner.outputs["rss_feed_cleaned"], colname=pipeline_name)

    airflow_config["catchup"] = False

    tfx_pipeline = pipeline.Pipeline(pipeline_name=pipeline_name,
                                     pipeline_root=pipeline_root,
                                     components=[crawler,
                                                 cleaner,
                                                 mongo],
                                     enable_cache=False,
                                     metadata_connection_config=metadata.sqlite_metadata_connection_config(
                                         metadata_path))

    return AirflowDagRunner(AirflowPipelineConfig(airflow_config)).run(tfx_pipeline)
