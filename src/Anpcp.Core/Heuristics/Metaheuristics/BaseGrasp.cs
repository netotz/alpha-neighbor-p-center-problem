using System.Diagnostics;

using Anpcp.Core.Heuristics.Constructives;
using Anpcp.Core.Heuristics.LocalSearches;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

namespace Anpcp.Core.Heuristics.Metaheuristics;

/// <summary>
/// Abstract base class for a Greedy Randomized Adaptive Search Procedure (GRASP).
/// </summary>
public abstract class BaseGrasp<TInstance, TConstructive, TLocalSearch>(
    int maxIterations,
    TimeSpan timeLimit,
    TConstructive constructive,
    TLocalSearch localSearch)
    where TInstance : BaseInstance
    where TConstructive : IConstructive<TInstance, AnpcpSolution>
    where TLocalSearch : ILocalSearch<TInstance, AnpcpSolution>
{
    /// <summary>
    /// Maximum number of iterations without improvement to stop.
    /// </summary>
    public int MaxIterations { get; } = maxIterations;
    public TimeSpan TimeLimit { get; } = timeLimit;
    public TConstructive Constructive { get; } = constructive;
    public TLocalSearch LocalSearch { get; } = localSearch;

    /// <summary>
    /// Current number of iterations without improvement.
    /// </summary>
    public int CurrentIterations { get; set; } = 0;
    public Stopwatch Stopwatch { get; set; } = new();
    /// <summary>
    /// Best solution found.
    /// </summary>
    public AnpcpSolution? BestSolution { get; set; }
    /// <summary>
    /// Number of times that GRASP found a new best solution.
    /// </summary>
    public int TotalImprovements { get; set; } = 0;

    public virtual AnpcpSolution Run()
    {
        Stopwatch.Restart();

        while (DoContinueIterating())
        {
            Iterate();
        }

        Stopwatch.Stop();

        return BestSolution!;
    }

    protected virtual void Iterate()
    {
        var solution = Constructive.Construct();
        var didLocalSearchImprove = LocalSearch.TryImprove();

        var improvedSolution = LocalSearch.Solution;

        if (BestSolution is null || improvedSolution.ObjectiveFunctionValue < BestSolution.ObjectiveFunctionValue)
        {
            BestSolution = improvedSolution;
            TotalImprovements++;

            CurrentIterations = 0;
        }
        else
        {
            CurrentIterations++;
        }
    }

    protected bool DoContinueIterating()
    {
        return CurrentIterations < MaxIterations && Stopwatch.Elapsed < TimeLimit;
    }
}
