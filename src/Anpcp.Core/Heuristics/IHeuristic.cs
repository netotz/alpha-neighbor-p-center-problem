﻿using Anpcp.Core.Instances;

namespace Anpcp.Core.Heuristics;

/// <summary>
/// Heuristic algorithm contract.
/// </summary>
public interface IHeuristic<TInstance>
    where TInstance : BaseInstance
{
    /// <summary>
    /// Problem parameter <c>p</c>, size of a solution <c>S</c>.
    /// </summary>
    /// <remarks><c>p = |S|</c></remarks>
    int PSize { get; }
    TInstance Instance { get; }
    /// <summary>
    /// Seed for random generators. If <c>null</c>, a random one is used.
    /// </summary>
    int? Seed { get; }
}
