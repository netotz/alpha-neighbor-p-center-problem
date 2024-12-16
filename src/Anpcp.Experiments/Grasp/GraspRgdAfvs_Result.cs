using Anpcp.Core.Heuristics.Constructives.Rgd;
using Anpcp.Core.Heuristics.LocalSearches.Afvs;
using Anpcp.Core.Heuristics.Metaheuristics;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

namespace Anpcp.Experiments.Grasp;

internal class GraspRgdAfvs_Result(
    int maxIterations,
    TimeSpan timeLimit,
    RandomizedGreedyDispersion<InstanceTwoSets> constructive,
    AlphaFastVertexSubstitution localSearch)
    : GraspRgdAfvs(maxIterations, timeLimit, constructive, localSearch)
{
    internal GraspResult Result { get; } = new()
    {
        FullName = constructive.Instance.Name,
        PValue = constructive.PSize,
        Alpha = localSearch.Alpha
    };
    /// <summary>
    /// Iteration number of the main loop. Doesn't reset like iterations without improvement.
    /// </summary>
    internal int GlobalIteration { get; private set; } = 0;

    public override AnpcpSolution Run()
    {
        Stopwatch.Restart();

        while (DoContinueIterating())
        {
            Iterate();

            GlobalIteration++;
        }

        Stopwatch.Stop();
        Result.Stopwatch = Stopwatch;

        return BestSolution!;
    }

    protected override void Iterate()
    {
        var solution = Constructive.Construct();

        var rgdOfv = solution.ObjectiveFunctionValue;
        Result.BestRgdOfv = Math.Min(
            Result.BestRgdOfv,
            rgdOfv);

        LocalSearch.SetSolution(solution);

        var didLocalSearchImprove = LocalSearch.TryImprove();

        var improvedSolution = LocalSearch.Solution;

        var afvsOfv = improvedSolution.ObjectiveFunctionValue;
        var afvsImprovement = 100 * Math.Abs(afvsOfv - rgdOfv) / rgdOfv;

        Result.AfvsMinImprovement = Math.Min(Result.AfvsMinImprovement, afvsImprovement);
        Result.AfvsMaxImprovement = Math.Max(Result.AfvsMaxImprovement, afvsImprovement);
        Result.AfvsImprovements.Add(afvsImprovement);

        if (BestSolution is null || afvsOfv < BestSolution.ObjectiveFunctionValue)
        {
            BestSolution = improvedSolution;

            Result.BestAfvsOfv = Math.Min(
                Result.BestAfvsOfv,
                afvsOfv);

            TotalImprovements++;

            CurrentIterations = 0;

            Result.LastImprovedIteration = GlobalIteration;
        }
        else
        {
            CurrentIterations++;
        }
    }
}
