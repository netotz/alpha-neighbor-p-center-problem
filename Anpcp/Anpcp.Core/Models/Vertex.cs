namespace Anpcp.Core.Models;

public record Vertex(int Index, int XCoord, int YCoord)
{
    /// <summary>
    /// Calculates the Euclidean distance to another vertex.
    /// </summary>
    public double DistanceTo(Vertex v)
    {
        return Math.Sqrt(
            Math.Pow(v.XCoord - XCoord, 2)
            + Math.Pow(v.YCoord - YCoord, 2));
    }
}
