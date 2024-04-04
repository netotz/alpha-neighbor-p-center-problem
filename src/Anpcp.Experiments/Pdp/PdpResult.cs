using Anpcp.Core.Heuristics.Constructives;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

namespace Anpcp.Experiments.Pdp;

public record PdpResult<TConstructive>(
    string InstanceName,
    TConstructive Constructive,
    PdpSolution Solution,
    TimeSpan HeuristicTime,
    TimeSpan? ObjectiveFunctionTime = null)
    where TConstructive : IConstructive<InstanceSameSet, PdpSolution>
{ }
