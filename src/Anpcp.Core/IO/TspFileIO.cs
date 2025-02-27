﻿using Anpcp.Core.Models;
using Anpcp.Core.Models.Enums;

namespace Anpcp.Core.IO;

/// <summary>
/// Reader for TSPLIB files.
/// </summary>
/// <remarks>
/// Currently supports files that specify <c>NODE_COORDS_SECTION</c> only.
/// </remarks>
public static class TspFileIO
{
    private static string NodeCoordSection { get; } = "NODE_COORD_SECTION";
    private static string Eof { get; } = "EOF";

    public static List<Vertex> ReadNodes(string filePath)
    {
        using var streamReader = new StreamReader(filePath);

        while (!streamReader.ReadLine()?.Contains(NodeCoordSection) ?? true) ;
        // all the next lines should be node coords

        var vertices = new List<Vertex>();
        var uniqueCoords = new HashSet<(int, int)>();

        var line = streamReader.ReadLine()?.Trim() ?? "";

        while (line != "" && !line.Contains(Eof))
        {
            // each line has format "i x y t?"
            var items = line.Trim().Split();
            // parse as double since some instances have
            // decimal (1.1) or scientific (1e+3) format
            var parsedItems = items.Select(double.Parse).ToArray();

            var index = (int)parsedItems[0];
            var xCoord = (int)parsedItems[1];
            var yCoord = (int)parsedItems[2];
            var type = parsedItems.Length == 4
                // if file includes vertex type
                ? (VertexType)parsedItems[3]
                : VertexType.Both;

            var isUnique = uniqueCoords.Add((xCoord, yCoord));
            if (isUnique)
            {
                vertices.Add(
                    new(index, xCoord, yCoord, type));
            }

            line = streamReader.ReadLine() ?? "";
        }

        return vertices;
    }
}
