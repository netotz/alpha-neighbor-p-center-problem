using Anpcp.Experiments;
using Anpcp.Experiments.Pdp;

// get repo path from environment variable, should be set by script
AppSettings.AnpcpRepoPath = new(
    Environment.GetEnvironmentVariable(
        nameof(AppSettings.AnpcpRepoPath)) ?? "");

var pdpExperiment = new PdpConstructivesExperiment();

pdpExperiment.Run();

pdpExperiment.WriteCsvResults();