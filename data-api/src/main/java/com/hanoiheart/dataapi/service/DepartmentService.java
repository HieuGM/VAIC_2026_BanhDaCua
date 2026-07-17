package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.DepartmentDto;
import com.hanoiheart.dataapi.entity.Department;
import com.hanoiheart.dataapi.repository.DepartmentRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DepartmentService {

    private final DepartmentRepository repository;

    public DepartmentService(DepartmentRepository repository) {
        this.repository = repository;
    }

    public List<DepartmentDto> list(Boolean activeOnly) {
        return repository.findAll().stream()
                .filter(d -> activeOnly == null || !activeOnly || Boolean.TRUE.equals(d.getIsActive()))
                .sorted(this::compareBySort)
                .map(this::toDto)
                .toList();
    }

    private int compareBySort(Department a, Department b) {
        int sa = a.getSortOrder() == null ? Integer.MAX_VALUE : a.getSortOrder();
        int sb = b.getSortOrder() == null ? Integer.MAX_VALUE : b.getSortOrder();
        return Integer.compare(sa, sb);
    }

    public DepartmentDto toDto(Department d) {
        return new DepartmentDto(d.getId(), d.getCode(), d.getName(), d.getNameEn(),
                d.getDescription(), d.getCampus(), d.getFloor(), d.getWorkingHours(),
                d.getPhone(), d.getSortOrder(), d.getIsActive());
    }
}
