using Anpcp.Experiments;
using Anpcp.Experiments.Pdp;

using Microsoft.Extensions.Configuration;

var config = new ConfigurationBuilder()
    .AddJsonFile("appSettings.json", false, true)
    .Build();

AppSettings.AppPaths = config
    .GetSection(nameof(AppPaths))
    .Get<AppPaths>();

var pdpExperiment = new PdpConstructivesExperiment();

pdpExperiment.Run();

pdpExperiment.WriteCsvResults();