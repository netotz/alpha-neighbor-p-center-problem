using Anpcp.Experiments;
using Anpcp.Experiments.Grasp;

// get repo path from environment variable, should be set by script
AppSettings.AnpcpRepoPath = new(
    Environment.GetEnvironmentVariable(
        nameof(AppSettings.AnpcpRepoPath)) ?? "");

//var pdpExperiment = new PdpConstructivesExperiment();

//pdpExperiment.Run();

//pdpExperiment.WriteCsvResults();

GraspExperiment_TwoSets.Run();
GraspExperiment_TwoSets.SaveCsvResults();
GraspExperiment_TwoSets.SaveTxtResults();

//GraspExperiment_SameSet.Run();
//GraspExperiment_SameSet.SaveCsvResults();
//GraspExperiment_SameSet.SaveTxtResults();
