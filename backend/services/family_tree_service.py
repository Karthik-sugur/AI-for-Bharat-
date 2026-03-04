"""
Family Tree Service
Reconstructs ownership lineage and family relationships
"""

import logging
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class FamilyTreeService:
    """Service for building family trees from ownership history"""
    
    def __init__(self, synthetic_data):
        """
        Initialize family tree service
        
        Args:
            synthetic_data: List of property records from JSON
        """
        self.data = synthetic_data
    
    def build_family_tree(self, property_id: str) -> Dict:
        """
        Build family tree from property ownership and family data
        
        Args:
            property_id: Property ID to build tree for
            
        Returns:
            Dictionary containing family tree structure with nodes and relationships
        """
        # Find property
        property_data = next((p for p in self.data if p.get('land_id') == property_id), None)
        
        if not property_data:
            return {
                'property_id': property_id,
                'error': 'Property not found',
                'nodes': [],
                'relationships': []
            }
        
        # Extract family tree if available
        family_tree_data = property_data.get('family_tree', {})
        ownership_chain = property_data.get('ownership_chain', property_data.get('owners', []))
        
        # Build nodes from family tree
        nodes = []
        relationships = []
        
        if family_tree_data and isinstance(family_tree_data, dict):
            # Process family tree structure
            nodes, relationships = self._process_family_tree_structure(family_tree_data, ownership_chain)
        else:
            # Build from ownership chain only
            nodes, relationships = self._build_from_ownership_chain(ownership_chain)
        
        # Identify key relationships
        inheritance_patterns = self.detect_inheritance_patterns(nodes, relationships, ownership_chain)
        family_relations = self.identify_family_relationships(nodes, relationships)
        
        return {
            'property_id': property_id,
            'current_owner': property_data.get('current_owner'),
            'nodes': nodes,
            'relationships': relationships,
            'inheritance_patterns': inheritance_patterns,
            'family_relations': family_relations,
            'generation_count': self._count_generations(nodes),
            'total_members': len(nodes)
        }
    
    def _process_family_tree_structure(self, family_data: Dict, ownership_chain: List) -> Tuple[List, List]:
        """
        Process structured family tree data
        
        Args:
            family_data: Family tree structure from JSON
            ownership_chain: List of ownership records
            
        Returns:
            Tuple of (nodes, relationships)
        """
        nodes = []
        relationships = []
        node_index = {}
        
        def process_node(person_data, parent_id=None, generation=1):
            person_name = person_data.get('name', 'Unknown')
            
            # Check if person owned the property
            owned_property = any(
                owner.get('owner_name') == person_name or owner.get('name') == person_name
                for owner in ownership_chain
            )
            
            node = {
                'id': len(nodes),
                'name': person_name,
                'generation': generation,
                'owned_property': owned_property,
                'relation': person_data.get('relation', 'Unknown'),
                'years_owned': person_data.get('years_owned'),
                'transfer_type': person_data.get('transfer_type')
            }
            
            nodes.append(node)
            node_index[person_name] = node['id']
            
            # Add parent relationship
            if parent_id is not None:
                relationships.append({
                    'from': parent_id,
                    'to': node['id'],
                    'type': person_data.get('relation', 'descendant')
                })
            
            # Process children
            children = person_data.get('children', [])
            for child in children:
                if isinstance(child, dict):
                    process_node(child, node['id'], generation + 1)
                elif isinstance(child, str):
                    # Simple child name
                    child_node = {
                        'id': len(nodes),
                        'name': child,
                        'generation': generation + 1,
                        'owned_property': False,
                        'relation': 'child'
                    }
                    nodes.append(child_node)
                    relationships.append({
                        'from': node['id'],
                        'to': child_node['id'],
                        'type': 'child'
                    })
        
        # Start processing from root
        if family_data:
            process_node(family_data, None, 1)
        
        return nodes, relationships
    
    def _build_from_ownership_chain(self, ownership_chain: List) -> Tuple[List, List]:
        """
        Build family tree from ownership chain only (fallback)
        
        Args:
            ownership_chain: List of ownership records
            
        Returns:
            Tuple of (nodes, relationships)
        """
        nodes = []
        relationships = []
        
        sorted_chain = sorted(ownership_chain, key=lambda x: x.get('from_year', x.get('year', 0)))
        
        for i, owner_data in enumerate(sorted_chain):
            node = {
                'id': i,
                'name': owner_data.get('owner_name', owner_data.get('name', 'Unknown')),
                'generation': i + 1,
                'owned_property': True,
                'from_year': owner_data.get('from_year', owner_data.get('year')),
                'to_year': owner_data.get('to_year'),
                'transfer_type': owner_data.get('transfer_type', owner_data.get('type')),
                'relation': 'owner'
            }
            nodes.append(node)
            
            # Link to previous owner
            if i > 0:
                relationships.append({
                    'from': i - 1,
                    'to': i,
                    'type': owner_data.get('transfer_type', 'transfer')
                })
        
        return nodes, relationships
    
    def identify_family_relationships(self, nodes: List, relationships: List) -> List[Dict]:
        """
        Identify family relationships between property owners
        
        Args:
            nodes: List of person nodes
            relationships: List of relationships
            
        Returns:
            List of identified family relationships
        """
        family_relations = []
        
        # Build relationship map
        rel_map = defaultdict(list)
        for rel in relationships:
            rel_map[rel['from']].append(rel)
        
        for node in nodes:
            if node.get('owned_property'):
                # Find relationships from this owner
                node_relationships = rel_map.get(node['id'], [])
                
                for rel in node_relationships:
                    target_node = next((n for n in nodes if n['id'] == rel['to']), None)
                    if target_node and target_node.get('owned_property'):
                        family_relations.append({
                            'from_owner': node['name'],
                            'to_owner': target_node['name'],
                            'relationship_type': rel['type'],
                            'generation_gap': target_node['generation'] - node['generation']
                        })
        
        return family_relations
    
    def detect_inheritance_patterns(self, nodes: List, relationships: List, ownership_chain: List) -> Dict:
        """
        Detect inheritance patterns in ownership transfer
        
        Args:
            nodes: List of person nodes
            relationships: List of relationships
            ownership_chain: Original ownership data
            
        Returns:
            Dictionary with inheritance pattern analysis
        """
        inheritance_transfers = []
        sale_transfers = []
        other_transfers = []
        
        for owner in ownership_chain:
            transfer_type = owner.get('transfer_type', owner.get('type', ''))
            
            if transfer_type in ['Inheritance', 'Will', 'Succession']:
                inheritance_transfers.append(owner)
            elif transfer_type in ['Sale', 'Purchase']:
                sale_transfers.append(owner)
            else:
                other_transfers.append(owner)
        
        total_transfers = len(ownership_chain)
        
        return {
            'total_transfers': total_transfers,
            'inheritance_count': len(inheritance_transfers),
            'sale_count': len(sale_transfers),
            'other_count': len(other_transfers),
            'inheritance_percentage': (len(inheritance_transfers) / total_transfers * 100) if total_transfers > 0 else 0,
            'is_family_succession': len(inheritance_transfers) > len(sale_transfers),
            'inheritance_chain': [
                {
                    'owner': t.get('owner_name', t.get('name')),
                    'year': t.get('from_year', t.get('year')),
                    'type': t.get('transfer_type', t.get('type'))
                }
                for t in inheritance_transfers
            ]
        }
    
    def _count_generations(self, nodes: List) -> int:
        """Count number of generations in family tree"""
        if not nodes:
            return 0
        return max(node.get('generation', 1) for node in nodes)
    
    def visualize_tree_text(self, family_tree: Dict) -> str:
        """
        Generate text-based visualization of family tree
        
        Args:
            family_tree: Result from build_family_tree()
            
        Returns:
            String with ASCII visualization
        """
        nodes = family_tree.get('nodes', [])
        relationships = family_tree.get('relationships', [])
        
        if not nodes:
            return "No family tree data available"
        
        output = []
        output.append("\nFamily Tree & Ownership Lineage")
        output.append("=" * 60)
        output.append(f"Current Owner: {family_tree.get('current_owner')}")
        output.append(f"Generations: {family_tree.get('generation_count')}")
        output.append(f"Total Members: {family_tree.get('total_members')}")
        output.append("=" * 60)
        output.append("")
        
        # Group by generation
        by_generation = defaultdict(list)
        for node in nodes:
            by_generation[node.get('generation', 1)].append(node)
        
        # Display by generation
        for gen in sorted(by_generation.keys()):
            output.append(f"Generation {gen}:")
            for node in by_generation[gen]:
                indent = "  " * (gen - 1)
                owner_marker = " [OWNER]" if node.get('owned_property') else ""
                output.append(f"{indent}├─ {node.get('name')}{owner_marker}")
                if node.get('transfer_type'):
                    output.append(f"{indent}│  Transfer: {node.get('transfer_type')}")
            output.append("")
        
        return "\n".join(output)
    
    def identify_ownership_risks(self, family_tree: Dict) -> List[Dict]:
        """
        Identify risks related to family ownership patterns
        
        Args:
            family_tree: Result from build_family_tree()
            
        Returns:
            List of risk indicators
        """
        risks = []
        
        inheritance_patterns = family_tree.get('inheritance_patterns', {})
        family_relations = family_tree.get('family_relations', [])
        
        # Check for broken inheritance chain
        if inheritance_patterns.get('inheritance_count', 0) == 0 and len(family_relations) > 0:
            risks.append({
                'type': 'Broken Inheritance Chain',
                'severity': 'Medium',
                'description': 'Family relationships exist but no inheritance transfers recorded'
            })
        
        # Check for multiple sales within family
        if inheritance_patterns.get('sale_count', 0) > inheritance_patterns.get('inheritance_count', 0):
            risks.append({
                'type': 'Multiple Sales',
                'severity': 'Low',
                'description': 'Property sold multiple times rather than inherited - verify all sale deeds'
            })
        
        # Check for fragmented ownership
        if family_tree.get('generation_count', 0) > 4:
            risks.append({
                'type': 'Multiple Generations',
                'severity': 'Medium',
                'description': 'Property passed through many generations - verify all inheritance claims'
            })
        
        return risks
    
    # Legacy methods for backward compatibility
    def build_family_tree_legacy(self, land_record):
        """
        Build family tree from land ownership history (legacy method)
        
        Args:
            land_record: Dictionary containing land record data
            
        Returns:
            Dictionary containing family tree structure
        """
        ownership_history = land_record.get('ownership_history', [])
        current_owner = land_record.get('current_owner')
        
        if not ownership_history:
            return {
                'current_owner': current_owner,
                'generations': 1,
                'total_transfers': 0,
                'tree': [{
                    'owner': current_owner,
                    'year': 'Current',
                    'type': 'Current Owner',
                    'generation': 1
                }]
            }
        
        # Build tree structure
        tree = []
        generation = len(ownership_history)
        
        # Add historical owners
        for i, hist in enumerate(sorted(ownership_history, key=lambda x: x.get('year', 0))):
            tree.append({
                'owner': hist.get('owner'),
                'year': hist.get('year'),
                'type': hist.get('type'),
                'generation': generation - i,
                'relation': self._infer_relation(hist.get('type'))
            })
        
        # Add current owner
        tree.append({
            'owner': current_owner,
            'year': 'Current',
            'type': 'Current Owner',
            'generation': 1,
            'relation': 'Current'
        })
        
        # Analyze transfer types
        transfer_analysis = self._analyze_transfers(ownership_history)
        
        return {
            'current_owner': current_owner,
            'generations': len(ownership_history) + 1,
            'total_transfers': len(ownership_history),
            'tree': tree,
            'transfer_analysis': transfer_analysis,
            'complexity_score': self._calculate_complexity(ownership_history)
        }
    
    def _infer_relation(self, transfer_type):
        """Infer family relation from transfer type"""
        relation_map = {
            'Inheritance': 'Child/Heir',
            'Sale': 'Purchaser',
            'Gift': 'Gift Recipient',
            'Partition': 'Co-owner',
            'Will': 'Beneficiary',
            'Settlement': 'Settlement Party'
        }
        return relation_map.get(transfer_type, 'Unknown')
    
    def _analyze_transfers(self, ownership_history):
        """Analyze patterns in ownership transfers"""
        
        transfer_types = defaultdict(int)
        for hist in ownership_history:
            transfer_type = hist.get('type', 'Unknown')
            transfer_types[transfer_type] += 1
        
        # Calculate inheritance chain
        inheritance_count = transfer_types.get('Inheritance', 0)
        sale_count = transfer_types.get('Sale', 0)
        
        return {
            'by_type': dict(transfer_types),
            'inheritance_count': inheritance_count,
            'sale_count': sale_count,
            'is_family_succession': inheritance_count > sale_count,
            'continuity_score': (inheritance_count / len(ownership_history) * 100) if ownership_history else 0
        }
    
    def _calculate_complexity(self, ownership_history):
        """Calculate complexity score of ownership chain"""
        
        if not ownership_history:
            return 0
        
        # Base complexity on number of transfers
        complexity = len(ownership_history) * 10
        
        # Add complexity for different transfer types
        transfer_types = set(hist.get('type') for hist in ownership_history)
        complexity += len(transfer_types) * 5
        
        # Add complexity for rapid transfers (within 5 years)
        rapid_transfers = 0
        sorted_history = sorted(ownership_history, key=lambda x: x.get('year', 0))
        for i in range(1, len(sorted_history)):
            year_diff = sorted_history[i].get('year', 0) - sorted_history[i-1].get('year', 0)
            if 0 < year_diff < 5:
                rapid_transfers += 1
        complexity += rapid_transfers * 15
        
        # Normalize to 0-100 scale
        return min(complexity, 100)
    
    def visualize_tree_legacy(self, family_tree):
        """
        Generate a text-based visualization of the family tree (legacy)
        
        Args:
            family_tree: Family tree structure from build_family_tree()
            
        Returns:
            String containing ASCII art family tree
        """
        tree_data = family_tree.get('tree', [])
        
        visualization = "\nOwnership Lineage:\n"
        visualization += "=" * 60 + "\n\n"
        
        for i, node in enumerate(tree_data):
            indent = "  " * (node.get('generation', 1) - 1)
            arrow = "└─> " if i > 0 else ""
            
            visualization += f"{indent}{arrow}{node.get('owner')}\n"
            visualization += f"{indent}    Year: {node.get('year')}\n"
            visualization += f"{indent}    Type: {node.get('type')}\n"
            visualization += f"{indent}    Relation: {node.get('relation', 'N/A')}\n\n"
        
        return visualization
    
    def identify_risks_legacy(self, family_tree):
        """
        Identify potential risks in the ownership chain (legacy)
        
        Args:
            family_tree: Family tree structure from build_family_tree()
            
        Returns:
            List of identified risks
        """
        risks = []
        
        # Check complexity
        if family_tree.get('complexity_score', 0) > 70:
            risks.append({
                'type': 'High Complexity',
                'severity': 'Medium',
                'description': 'Ownership chain is complex with multiple transfers'
            })
        
        # Check for rapid transfers
        tree_data = family_tree.get('tree', [])
        for i in range(1, len(tree_data)):
            curr_year = tree_data[i].get('year')
            prev_year = tree_data[i-1].get('year')
            
            if isinstance(curr_year, int) and isinstance(prev_year, int):
                if 0 < curr_year - prev_year < 3:
                    risks.append({
                        'type': 'Rapid Transfer',
                        'severity': 'Medium',
                        'description': f'Quick succession of ownership changes between {prev_year} and {curr_year}'
                    })
        
        # Check transfer type patterns
        transfer_analysis = family_tree.get('transfer_analysis', {})
        if transfer_analysis.get('sale_count', 0) > transfer_analysis.get('inheritance_count', 0):
            risks.append({
                'type': 'Multiple Sales',
                'severity': 'Low',
                'description': 'Property has been sold multiple times - verify all sale deeds'
            })
        
        return risks
