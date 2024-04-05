﻿using Anpcp.Core.Models;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core.Instances;

public abstract class BaseInstance
{
    public string Name { get; protected set; } = "";
    public Vertex[] Facilities { get; protected set; } = [];
    public IEnumerable<int> FacilitiesIndices => Facilities.Select(f => f.Index);
    public Vertex[] Users { get; protected set; } = [];
    public IEnumerable<int> UsersIndices => Users.Select(u => u.Index);
    /// <summary>
    /// Matrix of distances between users and facilities.
    /// </summary>
    public DistancesMatrix DistancesUF { get; protected set; } = new();
    /// <summary>
    /// Matrix of distances between facilities.
    /// </summary>
    public DistancesMatrix DistancesFF { get; protected set; } = new();
}